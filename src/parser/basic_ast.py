import abc
import itertools
import string
import typing
from dataclasses import dataclass
from llvmlite.ir import FunctionType

from src.parser.analyzers.is_const_expr import IsConstExpr
from src.parser.errors import *
from src.parser.basic_types import *
from src.parser.symbol_table import SymbolTable, Symbol, SymbolTableBlockType, SymbolTableLLVMEntry
from llvmlite import ir, binding
from src.parser.global_constructor import GlobalConstructor, label_suffix, gep_opaque


class Expr(abc.ABC):
    def __init__(self):
        self.type = Type()

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        return self

    def codegen(self, symbol_table: SymbolTable, lvalue: bool = True):
        return self


class Statement(abc.ABC):

    def codegen(self, symbol_table: SymbolTable):
        return self


@dataclass
class Varname:
    pos: pe.Position
    name: str
    type: Type

    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, type = attrs
        cvarname, ctype = coords
        return Varname(cvarname, varname, type)

    def __eq__(self, other):
        if isinstance(other, Varname):
            return self.name == other.name and self.type == other.type
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def mangle_str(self):
        if len(self.type.name) == 1 or self.type.name == 'String':
            return f"{self.name}{self.type.mangle_suff}"

    def __str__(self):
        if len(self.type.name) == 1 or self.type.name == 'String':
            return f"{self.name}{self.type.name}"
        else:
            return f"{self.type} {self.name}"


@dataclass
class ConstExpr(Expr):
    pos: pe.Position
    value: typing.Any
    type: Type

    @staticmethod
    @pe.ExAction
    def createInt(attrs, coords, res_coord):
        value = attrs[0]
        cvalue = coords[0]
        return ConstExpr(cvalue.start, value, IntegerT())

    @staticmethod
    @pe.ExAction
    def createFl(attrs, coords, res_coord):
        value = attrs[0]
        cvalue = coords[0]
        return ConstExpr(cvalue.start, value, FloatT())

    @staticmethod
    @pe.ExAction
    def createStr(attrs, coords, res_coord):
        value = attrs[0]
        cvalue = coords[0]
        value = value[1:-1].replace("\\n", '\n').replace("\\t", ' ' * 4)
        return ConstExpr(cvalue.start, value, StringT(length=len(value)))

    def codegen(self, symbol_table: SymbolTable, lvalue: bool = True):
        if self.type == StringT():
            if symbol_table.block_type == SymbolTableBlockType.GlobalBlock:
                return ir.Constant(self.type.llvm_type(), [ord(char) for char in self.value] + [0])
            else:
                if hasattr(self, "__cached_var"):
                    return self.__cached_var
                else:
                    if hasattr(ConstExpr, "static_cnt"):
                        ConstExpr.static_cnt += 1
                    else:
                        ConstExpr.static_cnt = 1
                    var = ir.GlobalVariable(symbol_table.llvm.module, self.type.llvm_type(), f".str.{ConstExpr.static_cnt}")
                    var.initializer = ir.Constant(self.type.llvm_type(), [ord(char) for char in self.value] + [0])
                    self.__cached_var = var
                    return self.__cached_var
        elif self.type == FloatT():
            return ir.Constant(self.type.llvm_type(), float(self.value))
        else:
            return ir.Constant(self.type.llvm_type(), int(self.value))

    def __str__(self):
        return str(self.value)



@dataclass
class Variable:
    pos: pe.Position
    name: Varname
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname = attrs[0]
        cvarname = coords[0]
        return Variable(cvarname.start, varname, varname.type)

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        lookup_result = symbol_table.lookup(self.symbol(), by_origin=False)
        name_lookup_result = symbol_table.lookup(self.symbol(), by_type=False, by_origin=False)
        if not name_lookup_result and not lvalue:
            raise UndefinedSymbol(self.pos, self.name)
        if not lookup_result and not lvalue:
            self.type = name_lookup_result.type
            if isinstance(self.type, ArrayT):
                return Array(self.pos, self.name, self.type, self.type.size).relax(symbol_table)
        return self

    def symbol(self):
        return Symbol(self.name, self.type, False)


    """ I assume that would be called only from expressions codegen """
    def codegen(self, symbol_table, lvalue: bool = False):
        lookup_result = symbol_table.lookup(self.symbol(), by_origin=False)
        if lvalue:
            return lookup_result.llvm_obj
        else:
            return symbol_table.llvm.builder.load(lookup_result.llvm_obj, f"{self.name.mangle_str()}.load")


@dataclass
class Array(Variable):
    size: list[Expr]

    @staticmethod
    @pe.ExAction
    def create_variable(attrs, coords, res_coord):
        varname, sizes = attrs
        cvarname, cop, cexpr, ccp = coords
        return Array(cvarname.start, varname, ArrayT(varname.type, sizes), sizes)

    @staticmethod
    @pe.ExAction
    def create_param(attrs, coords, res_coord):
        varname, dimensions = attrs
        cvarname, cop, cexpr, ccp = coords
        size = [0] * dimensions
        expression_sizes = [ConstExpr(cop.start, 0, IntegerT())] * dimensions
        return Array(cvarname.start, varname, ArrayT(varname.type, size), expression_sizes)

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        if isinstance(self.size[0], int):
            return self
        for idx, expr in enumerate(self.size):
            self.size[idx] = expr.relax(symbol_table, lvalue=False)
            if not isinstance(self.size[idx].type, IntegralT):
                raise ArrayNotIntInit(self.pos, self.size[idx].type)
        return self

    """ I assume that would be called only from expressions codegen """

    def codegen(self, symbol_table, lvalue: bool = False):
        lookup_result = symbol_table.lookup(self.symbol(), by_origin=False)
        if lvalue:
            return lookup_result.llvm_obj
        else:
            if self.type.is_function_param:
                return ArrayIndex.get_func_ptr(symbol_table.llvm.builder, lookup_result.llvm_obj, [ir.Constant(ir.IntType(32), 0)])
            else:
                return ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, lookup_result.llvm_obj, [ir.Constant(ir.IntType(32), 0)])

@dataclass
class ArrayReference(Variable):
    pass

@dataclass
class FunctionProto:
    pos: pe.Position
    name: Varname
    args: list[Variable]
    type: ProcedureT

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, args = attrs
        cfunc_kw, cvar, cop, cparams, ccp = coords
        return FunctionProto(cvar.start, name, args, ProcedureT(name.type, [arg.type for arg in args]))

    @staticmethod
    def construct(varname: Varname, args: list[Variable]):
        return FunctionProto(pe.Position(-1,-1,-1), varname, args, ProcedureT(varname.type, [arg.type for arg in args]))

    def relax(self, symbol_table: SymbolTable):
        names = [self.name]
        for idx, var in enumerate(self.args):
            if var.name in names:
                raise RedefinitionError(var.pos, var.name, names[names.index(var.name)].pos)
            if isinstance(var.type, ArrayT):
                var.type.is_function_param = True
        return self

    def codegen(self, symbol_table: SymbolTable) -> tuple[FunctionType, list[Symbol]]:
        arguments = []
        symbols = []
        arg_list = self.args
        for arg in arg_list:
            arguments.append(arg.type.llvm_type())
            symbols.append(Symbol(arg.name, arg.type))
            if isinstance(arg.type, ArrayT):
                for len_idx in range(len(arg.type.size)):
                    arguments.append(ir.IntType(32))
                    symbols.append(Symbol(Varname(pe.Position(), f"{arg.name.name}.len.{len_idx+1}", IntegerT()), IntegerT()))
        return ir.FunctionType(self.type.retT.llvm_type(), arguments), symbols



@dataclass
class FunctionDecl:
    pos: pe.Position
    proto: FunctionProto
    external: bool

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto = attrs[0]
        cdecl_kw, cproto = coords
        return FunctionDecl(cdecl_kw.start, proto, True)

    def relax(self, symbol_table: SymbolTable):
        symbol = self.symbol()
        lookup_result = symbol_table.lookup(symbol, local=True, by_origin=False)
        if lookup_result and lookup_result.external:
            raise RedefinitionError(self.pos, self.proto.name, lookup_result.name.pos)
        if not lookup_result:
            symbol_table.add(symbol)
        self.proto = self.proto.relax(symbol_table)
        return self

    def symbol(self):
        return Symbol(self.proto.name, self.proto.type, self.external)

    def codegen(self, symbol_table: SymbolTable) -> ir.Function:
        if self.proto.name.name == "Len" and self.proto.name.type == IntegerT():
            return None
        function_proto, symbols = self.proto.codegen(symbol_table)
        func = ir.Function(symbol_table.llvm.module, function_proto, self.proto.name.name)
        for arg_symbol, arg in zip(symbols, func.args):
            arg.name = arg_symbol.name.name
        symbol_table.add(self.symbol().assoc(func))
        return func


@dataclass
class FunctionDef:
    pos: pe.Position
    proto: FunctionProto
    body: list[Statement]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto, stmts = attrs
        cfunproto, cbody, cend_kw, cfun_kw = coords
        return FunctionDef(cfunproto.start, proto, stmts)

    def relax(self, symbol_table: SymbolTable):
        symbol = self.symbol()
        lookup_result = symbol_table.lookup(symbol, local=True, by_origin=False)
        if lookup_result:
            if not lookup_result.external:
                raise RedefinitionError(self.pos, self.proto.name, lookup_result.name.pos)
            else:
                lookup_result.external = False
        else:
            symbol_table.add(symbol)
        self.proto.relax(symbol_table)
        body_symbol_table = symbol_table.new_local(SymbolTableBlockType.FunctionBlock)
        func_ret_variable = Variable(self.proto.name.pos, self.proto.name, self.proto.type.retT)
        body_symbol_table.add(func_ret_variable.symbol())
        for var in self.proto.args:
            body_symbol_table.add(var.symbol())
        for idx, stmt in enumerate(self.body):
            self.body[idx] = stmt.relax(body_symbol_table)
        return self

    def symbol(self):
        return Symbol(self.proto.name, self.proto.type, False)

    def codegen(self, symbol_table: SymbolTable) -> ir.Function:
        function_proto, symbols = self.proto.codegen(symbol_table)
        func = ir.Function(symbol_table.llvm.module, function_proto, self.proto.name.name)
        symbol_table.add(self.symbol().assoc(func))

        for arg_symbol, arg in zip(symbols, func.args):
            arg.name = arg_symbol.name.name
        entry_block = func.append_basic_block(name="entry")

        return_block = func.append_basic_block(name="return")

        builder = ir.IRBuilder(entry_block)
        body_symbol_table = symbol_table.new_local(SymbolTableBlockType.FunctionBlock,
                                                   llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module, builder, func))

        ret_var = Variable(self.proto.name.pos, self.proto.name, self.proto.type.retT)
        ret_val = builder.alloca(ret_var.type.llvm_type(), 1, ret_var.name.name)
        body_symbol_table.add(ret_var.symbol().assoc(ret_val))
        builder.store(ir.Constant(self.proto.type.retT.llvm_type(), self.proto.type.retT.default_value()), ret_val)
        """ 
        Maybe store default value???
        """
        for arg_symbol, arg in zip(symbols, func.args):
            alloc_instr = builder.alloca(arg.type, 1, arg.name)
            body_symbol_table.add(arg_symbol.assoc(alloc_instr))
            builder.store(arg, alloc_instr)

        for stmt in self.body:
            stmt.codegen(body_symbol_table)

        if builder.block.terminator is None:
            builder.branch(return_block)

        return_builder = ir.IRBuilder(return_block)
        return_builder.ret(return_builder.load(ret_val))
        return func



@dataclass
class SubroutineProto:
    pos: pe.Position
    name: Varname
    args: list[Variable]
    type: ProcedureT

    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, args = attrs
        csub_kw, cvar, cop, cparams, ccp = coords
        varname = Varname(cvar.start, name, VoidT())
        return SubroutineProto(csub_kw.start, varname, args, ProcedureT(VoidT(), [arg.type for arg in args]))

    def relax(self, symbol_table: SymbolTable):
        names = [self.name]
        for idx, var in enumerate(self.args):
            if var.name in names:
                raise RedefinitionError(var.pos, var.name, names[names.index(var.name)].pos)
            if isinstance(var.type, ArrayT):
                var.type.is_function_param = True
        return self

    def codegen(self, symbol_table: SymbolTable) -> tuple[FunctionType, list[Symbol]]:
        arguments = []
        symbols = []
        for arg in self.args:
            arguments.append(arg.type.llvm_type())
            symbols.append(Symbol(arg.name, arg.type))
            if isinstance(arg.type, ArrayT):
                for len_idx in range(len(arg.type.size)):
                    arguments.append(ir.IntType(32))
                    symbols.append(
                        Symbol(Varname(pe.Position(), f"{arg.name.name}.len.{len_idx + 1}", IntegerT()), IntegerT()))
        return ir.FunctionType(self.type.retT.llvm_type(), arguments), symbols

@dataclass
class SubroutineDecl:
    pos: pe.Position
    proto: SubroutineProto
    external: bool

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto = attrs[0]
        cdecl_kw, cproto = coords
        return SubroutineDecl(cdecl_kw.start, proto, True)

    def relax(self, symbol_table: SymbolTable):
        symbol = self.symbol()
        lookup_result = symbol_table.lookup(symbol, local=True, by_origin=False)
        if lookup_result and lookup_result.external:
            raise RedefinitionError(self.pos, self.proto.name, lookup_result.name.pos)
        if not lookup_result:
            symbol_table.add(symbol)
        self.proto = self.proto.relax(symbol_table)
        return self

    def symbol(self):
        return Symbol(self.proto.name, self.proto.type, self.external)

    def codegen(self, symbol_table) -> ir.Function:
        subroutine_proto, symbols = self.proto.codegen(symbol_table)
        func = ir.Function(symbol_table.llvm.module, subroutine_proto, self.proto.name.name)
        for arg_symbol, arg in zip(symbols, func.args):
            arg.name = arg_symbol.name.name
        symbol_table.add(self.symbol().assoc(func))
        return func


@dataclass
class SubroutineDef:
    pos: pe.Position
    proto: SubroutineProto
    body: list[Statement]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto, stmts = attrs
        csubproto, cbody, cend_kw, csub_kw = coords
        return SubroutineDef(csubproto.start, proto, stmts)

    def relax(self, symbol_table: SymbolTable):
        symbol = Symbol(self.proto.name, self.proto.type, False)
        lookup_result = symbol_table.lookup(symbol, local=True, by_origin=False)
        if lookup_result:
            if not lookup_result.external:
                raise RedefinitionError(self.pos, self.proto.name, lookup_result.name.pos)
            else:
                lookup_result.external = False
        else:
            symbol_table.add(symbol)
        self.proto.relax(symbol_table)
        body_symbol_table = symbol_table.new_local(SymbolTableBlockType.FunctionBlock)
        for var in self.proto.args:
            body_symbol_table.add(var.symbol())
        for idx, stmt in enumerate(self.body):
            self.body[idx] = stmt.relax(body_symbol_table)
        return self

    def symbol(self):
        return Symbol(self.proto.name, self.proto.type, False)

    def codegen(self, symbol_table) -> ir.Function:
        subroutine_proto, symbols = self.proto.codegen(symbol_table)
        sub = ir.Function(symbol_table.llvm.module, subroutine_proto, self.proto.name.name)
        symbol_table.add(self.symbol().assoc(sub))

        for arg_symbol, arg in zip(symbols, sub.args):
            arg.name = arg_symbol.name.name
        entry_block = sub.append_basic_block(name="entry")

        return_block = sub.append_basic_block(name="return")
        return_builder = ir.IRBuilder(return_block)
        return_builder.ret_void()

        builder = ir.IRBuilder(entry_block)
        body_symbol_table = symbol_table.new_local(SymbolTableBlockType.FunctionBlock,
                                                   llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module, builder, sub))

        for arg_symbol, arg in zip(symbols, sub.args):
            alloc_instr = builder.alloca(arg.type, 1, arg.name)
            body_symbol_table.add(arg_symbol.assoc(alloc_instr))
            builder.store(arg, alloc_instr)

        for stmt in self.body:
            stmt.codegen(body_symbol_table)
        if builder.block.terminator is None:
            builder.branch(return_block)
        return sub


@dataclass
class InitializerList:
    pos: pe.Position
    values: list[Expr | list]
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        vals = attrs[0]
        cop, cvalues, ccp = coords
        return InitializerList(cop.start, vals, VoidT())

    def relax(self, symbol_table: SymbolTable, lvalue: bool = False):
        common_type = None if len(self.values) == 0 else type(self.values[0])
        if not common_type:
            return self
        for val in self.values:
            if common_type != type(val):
                raise InappropriateInitializerList(self.pos, common_type, type(val))
        self.size()
        for idx, val in enumerate(self.values):
            self.values[idx] = val.relax(symbol_table, lvalue=False)
        common_type = self.values[0].type
        for val in self.values:
            if common_type != val.type:
                raise InappropriateInitializerList(self.pos, common_type, val.type)
        self.type = common_type
        return self

    def size(self):
        if len(self.values) == 0:
            return 0
        if isinstance(self.values[0], InitializerList):
            common_sz = self.values[0].size()
            for val in self.values:
                val_size = val.size()
                if common_sz != val_size:
                    raise InitializerListDimensionMismatch(self.pos, common_sz, val_size)
            return [len(self.values)] + common_sz
        else:
            return [len(self.values)]

    def __getitem__(self, item):
        return self.values[item]


@dataclass
class VariableDecl:
    pos: pe.Position
    variable: Variable
    init_value: typing.Optional[Expr | InitializerList | None]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        var, var_ini = attrs[0], attrs[1] if len(attrs) > 1 else None
        cdim_kw, cvar, cvar_init = coords
        return VariableDecl(cdim_kw.start, var, var_ini)

    def relax(self, symbol_table: SymbolTable):
        if (lookup_result := symbol_table.lookup(self.variable.symbol(), local=True, by_type=False, by_origin=False)) is not None:
            raise RedefinitionError(self.pos, self.variable.name, lookup_result.name.pos)
        if self.init_value:
            self.init_value = self.init_value.relax(symbol_table)
            if isinstance(self.variable, Array):
                if not self.init_value.type.castable_to(self.variable.type.type):
                    raise ConversionError(self.pos, self.init_value.type, self.variable.type.type)
                if isinstance(self.init_value, Expr):
                    raise InappropriateInitializerList(self.pos, f"InitializerList{{{self.variable.type}}}", self.init_value)
                else:
                    self.variable = self.variable.relax(symbol_table)
                    self.variable.size = self.__check_sizes(self.variable.size, self.init_value.size())
                    self.variable.type.size = self.variable.size
                    symbol_table.add(self.variable.symbol())
            else:
                if not self.init_value.type.castable_to(self.variable.type):
                    raise ConversionError(self.pos, self.init_value.type, self.variable.type)
                if isinstance(self.init_value, InitializerList):
                    sz = self.init_value.size()
                    self.variable = Array(self.variable.pos, self.variable.name, ArrayT(self.variable.type, sz), sz)
                    symbol_table.add(self.variable.symbol())
                else:
                    if isinstance(self.init_value, ConstExpr) and self.variable.type != self.init_value.type:
                        self.init_value = ConstExpr(self.init_value.pos, self.init_value.value, self.variable.type)
                    symbol_table.add(self.variable.symbol())
        else:
            if isinstance(self.variable, Array):
                if isinstance(self.variable.size[0], int):
                    raise InitializationUndefinedLengthError(self.pos, self.variable.size)
                for idx, sz in enumerate(self.variable.size):
                    if not (isinstance(sz, ConstExpr) and isinstance(sz.type, IntegralT)):
                        raise InitializationUndefinedLengthError(self.pos, self.variable.size)
                    self.variable.size[idx] = self.variable.size[idx].value
            symbol_table.add(self.variable.symbol())
            self.variable = self.variable.relax(symbol_table)
        return self

    def __check_sizes(self, expected_size, given_size):
        if len(expected_size) != len(given_size):
            raise InitializationLengthMismatchError(self.pos, expected_size, given_size)
        for sz in expected_size:
            if not IsConstExpr(sz):
                raise InitializationNonConstSize(sz.pos, sz)
            elif sz.value <= 0:
                raise InitializationNegativeSize(sz.pos, sz)
        result = [sz.value for sz in expected_size]
        for i in range(len(expected_size)):
            if expected_size[i] == 0 and given_size[i] == 0:
                raise InitializationUndefinedLengthError(self.pos, expected_size)
            elif expected_size[i] != 0 and given_size[i] != 0:
                if result[i] != given_size[i]:
                    raise InitializationLengthMismatchError(self.pos, expected_size, given_size)
            result[i] = max(result[i], given_size[i])
        return result

    def codegen(self, symbol_table: SymbolTable):
        if symbol_table.block_type != SymbolTableBlockType.GlobalBlock:
            alloc_instr = symbol_table.llvm.builder.alloca(self.variable.type.llvm_type(), 1, self.variable.name.mangle_str())
            if self.init_value:
                if isinstance(self.init_value, InitializerList):
                    for idx in itertools.product(*[range(s) for s in self.variable.size]):
                        val = self.init_value.values[idx[0]]
                        for i in range(1, len(idx)):
                            val = val[idx[i]]
                        arr_ptr = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, alloc_instr, list(idx))
                        relaxed = self.cast_init_value(self.variable.type.type, val, symbol_table, symbol_table.llvm.builder)
                        symbol_table.llvm.builder.store(relaxed, arr_ptr)
                else:
                    buffer = self.cast_init_value(self.variable.type, self.init_value, symbol_table, symbol_table.llvm.builder)
                    symbol_table.llvm.builder.store(buffer, alloc_instr)
            symbol_table.add(self.variable.symbol().assoc(alloc_instr))
            return alloc_instr
        else:
            var = ir.GlobalVariable(symbol_table.llvm.module, self.variable.type.llvm_type(), self.variable.name.mangle_str())
            if self.init_value:
                if isinstance(self.init_value, ConstExpr) and self.variable.type == self.init_value.type:
                    var.initializer = self.cast_init_value(self.variable.type, self.init_value, symbol_table, symbol_table.llvm.builder)
                elif isinstance(self.init_value, (InitializerList, Expr)):
                    sub_proto = ir.FunctionType(ir.VoidType(), [])
                    sub = ir.Function(symbol_table.llvm.module,
                                      sub_proto,
                                      f"__bas_global_var_init.{self.variable.name.mangle_str()}")
                    block = sub.append_basic_block(name="entry")
                    init_builder = ir.IRBuilder(block)
                    symbol_table.llvm.builder = init_builder
                    if isinstance(self.init_value, Expr):
                        var.initializer = ir.Constant(self.init_value.type.llvm_type(), self.init_value.type.default_value())
                        buffer = self.cast_init_value(self.variable.type, self.init_value, symbol_table, symbol_table.llvm.builder)
                        symbol_table.llvm.builder.store(buffer, var)
                    else:
                        var.initializer = ir.Constant(self.variable.type.llvm_type(), self.variable.type.default_value())
                        for idx in itertools.product(*[range(s) for s in self.variable.size]):
                            val = self.init_value.values[idx[0]]
                            for i in range(1, len(idx)):
                                val = val[idx[i]]
                            const_expr_idx = [ir.Constant(ir.IntType(32), idx_idx) for idx_idx in idx]
                            arr_ptr = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, var, const_expr_idx)
                            relaxed = self.cast_init_value(self.variable.type.type, val, symbol_table, symbol_table.llvm.builder)
                            symbol_table.llvm.builder.store(relaxed, arr_ptr)
                    symbol_table.llvm.builder.ret_void()
                    lookup_result = symbol_table.lookup(Program.global_constructor_symbol(), by_type=False, by_origin=False)
                    if isinstance(lookup_result.llvm_obj, ir.Function):
                        glob_builder = ir.IRBuilder(lookup_result.llvm_obj.entry_basic_block)
                        with glob_builder.goto_entry_block():
                            glob_builder.call(sub, [])
                    else:
                        raise RuntimeError("llvm_obj isn't ir.Function")
                    symbol_table.llvm.builder = None
            symbol_table.add(self.variable.symbol().assoc(var))
            return var

    def cast_init_value(self, tp, val, symbol_table: SymbolTable, builder: ir.IRBuilder):
        value = val.codegen(symbol_table, False)
        if tp != val.type:
            value = val.type.cast_to(tp, builder)(value)
        return value


@dataclass
class FuncCallOrArrayIndex:
    pos: pe.Position
    name: Varname
    args: list[Expr]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, args = attrs
        cvarname, cop, cargs, ccp = coords
        return FuncCallOrArrayIndex(cvarname.start, varname, args)

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        lookup_result = symbol_table.lookup(Symbol(self.name, self.name.type), by_type=False, by_origin=False)
        if not lookup_result:
            raise UndefinedSymbol(self.pos, self.name)
        else:
            if isinstance(lookup_result.type, ArrayT):
                result = ArrayIndex(self.pos, self.name, self.args, self.name.type)
                return result.relax(symbol_table)
            elif isinstance(lookup_result.type, ProcedureT):
                result = FuncCall(self.pos, self.name, self.args, self.name.type)
                return result.relax(symbol_table)
        return self


@dataclass
class PrintCall:
    pos: pe.Position
    expr: list[Expr]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        args = attrs[0]
        cprint, cargs = coords
        return PrintCall(cprint.start, args)

@dataclass
class FuncCall:
    pos: pe.Position
    name: Varname
    args: list[Expr]
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        func_name, args = attrs
        cfunc, cop, cargs, ccp = coords
        if isinstance(func_name, str):
            func_name = Varname(cfunc.start, func_name, VoidT())
        return FuncCall(cfunc.start, func_name, args, func_name.type)

    @staticmethod
    @pe.ExAction
    def create_print(attrs, coords, res_coord):
        args = attrs[0]
        cprint, cargs = coords
        func_name = Varname(cprint.start, "Print", VoidT())
        return FuncCall(cprint.start, func_name, args, func_name.type)

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        for idx, arg in enumerate(self.args):
            self.args[idx] = arg.relax(symbol_table, False)
        if self.name.name == "Print":
            for arg in self.args:
                if not isinstance(arg.type, (NumericT, ConstantStringT, PointerT)):
                    raise UndefinedFunction(self.pos, self.name, ProcedureT(VoidT(), [arg.type]))
        else:
            lookup_result = symbol_table.lookup(self.symbol(), by_origin=False, accumulate=True)
            name_lookup_result = symbol_table.lookup(self.symbol(), by_type=False, by_origin=False, accumulate=True)
            if name_lookup_result is None:
                raise UndefinedSymbol(self.pos, self.name)
            func_subst = None
            for symb in name_lookup_result:
                if self.symbol().type.castable_to(symb.type):
                    func_subst = symb
                    break
            if not lookup_result and not func_subst:
                raise UndefinedFunction(self.pos, self.name, self.symbol().type)
        return self

    def symbol(self):
        return Symbol(self.name, ProcedureT(self.name.type, [arg.type for arg in self.args]))

    def print_symbols(self):
        return [Symbol(self.name, ProcedureT(self.name.type, [arg.type])) for arg in self.args]

    def codegen(self, symbol_table: SymbolTable, lvalue: bool = True):
        const_zero = ir.Constant(ir.IntType(32), 0)
        const_one = ir.Constant(ir.IntType(32), 1)
        if self.name.name == "Print":
            for arg in self.args:
                lookup_result = symbol_table.lookup(Program.print_symbol(arg.type))
                value = arg.codegen(symbol_table, False)
                if isinstance(value, ir.GlobalVariable) and isinstance(arg.type, StringT):
                    value = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, value, [const_zero])
                symbol_table.llvm.builder.call(lookup_result.llvm_obj, [value])
        elif self.name.name == "Len" and self.name.type == IntegerT():
            arg = self.args[0].symbol()
            len_val = None
            if isinstance(self.args[0], Array):
                len_val = symbol_table.lookup(Symbol(Varname(pe.Position(), f"{arg.name.name}.len.1", IntegerT()), IntegerT()))
            elif isinstance(self.args[0], ArrayIndex):
                lookup_result = symbol_table.lookup(arg)
                idx = len(lookup_result.type.size) - len(arg.type.size) + 1
                len_val = symbol_table.lookup(Symbol(Varname(pe.Position(), f"{arg.name.name}.len.{idx}", IntegerT()), IntegerT()))
            return symbol_table.llvm.builder.load(len_val.llvm_obj)
        else:
            lookup_result = symbol_table.lookup(self.symbol(), by_origin=False, accumulate=True)
            name_lookup_result = symbol_table.lookup(self.symbol(), by_type=False, by_origin=False, accumulate=True)
            func = None
            args = []
            if lookup_result:
                func = lookup_result[0].llvm_obj
                for arg in self.args:
                    arg_value = arg.codegen(symbol_table, False)
                    if isinstance(arg.type, StringT) and isinstance(arg_value, ir.GlobalVariable):
                        arg_value = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, arg_value, [const_zero])
                    args.append(arg_value)
                    if isinstance(arg, Array):
                        if arg.type.is_function_param:
                            arg_symbol = arg.symbol()
                            len_val = None
                            if isinstance(arg, Array):
                                len_val = symbol_table.lookup(Symbol(Varname(pe.Position(), f"{arg_symbol.name.name}.len.1", IntegerT()), IntegerT()))
                            elif isinstance(arg, ArrayIndex):
                                lookup_result = symbol_table.lookup(arg_symbol)
                                idx = len(lookup_result.type.size) - len(arg_symbol.type.size) + 1
                                len_val = symbol_table.lookup(Symbol(Varname(pe.Position(), f"{arg_symbol.name.name}.len.{idx}", IntegerT()),IntegerT()))
                            args.append(symbol_table.llvm.builder.load(len_val.llvm_obj))
                        else:
                            for sz in arg.size:
                                args.append(ir.Constant(ir.IntType(32), sz))
            else:
                """ Casting types somehow """
                found_symb = None
                for symb in name_lookup_result:
                    if self.symbol().type.castable_to(symb.type):
                        found_symb = symb
                        func = symb.llvm_obj
                        break
                for call_arg_type, func_arg_type, call_arg in zip(self.symbol().type.argsT, found_symb.type.argsT, self.args):
                    arg = call_arg.codegen(symbol_table, False)
                    if call_arg_type != func_arg_type:
                        arg = call_arg_type.cast_to(func_arg_type, symbol_table.llvm.builder)(arg)
                    if isinstance(call_arg.type, StringT) and isinstance(arg, ir.GlobalVariable):
                        arg = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, arg, [const_zero])
                    args.append(arg)
                    if isinstance(call_arg, Array):
                        if call_arg.type.is_function_param:
                            arg_symbol = call_arg.symbol()
                            len_val = None
                            if isinstance(call_arg, Array):
                                len_val = symbol_table.lookup(Symbol(Varname(pe.Position(), f"{arg_symbol.name.name}.len.1", IntegerT()), IntegerT()))
                            elif isinstance(call_arg, ArrayIndex):
                                lookup_result = symbol_table.lookup(arg_symbol)
                                idx = len(lookup_result.type.size) - len(arg_symbol.type.size) + 1
                                len_val = symbol_table.lookup(Symbol(Varname(pe.Position(), f"{arg_symbol.name.name}.len.{idx}", IntegerT()),IntegerT()))
                            args.append(symbol_table.llvm.builder.load(len_val.llvm_obj))
                        else:
                            for sz in call_arg.size:
                                args.append(ir.Constant(ir.IntType(32), sz))
            if isinstance(func, ir.Function):
                name = "call"
                if func.ftype.return_type == ir.VoidType():
                    name = ""
                return symbol_table.llvm.builder.call(func, args, name)


@dataclass
class ArrayIndex:
    pos: pe.Position
    name: Varname
    args: list[Expr]
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pass

    def relax(self, symbol_table: SymbolTable):
        for idx, arg in enumerate(self.args):
            self.args[idx] = arg.relax(symbol_table)
            if not isinstance(self.args[idx].type, IntegralT):
                raise ArrayNotIntIndexing(self.pos, self.args[idx].type)
        lookup_result = symbol_table.lookup(Symbol(self.name, self.name.type), by_type=False, by_origin=False)
        if not lookup_result:
            raise UndefinedSymbol(self.pos, self.name)
        if len(self.args) != len(lookup_result.type.size):
            if len(self.args) > len(lookup_result.type.size):
                raise ArrayIndexingDimensionMismatchError(self.pos, len(lookup_result.type.size), len(self.args))
            else:
                self.type = ArrayT(self.name.type,
                                   lookup_result.type.size[len(self.args):len(lookup_result.type.size)],
                                   lookup_result.type.is_function_param)
        return self

    def symbol(self):
        return Symbol(self.name, self.name.type)

    def codegen(self, symbol_table: SymbolTable, lvalue: bool = True):
        lookup_result = symbol_table.lookup(Symbol(self.name, self.name.type), by_type=False, by_origin=False)
        if isinstance(lookup_result.llvm_obj, (ir.AllocaInstr, ir.GlobalVariable)):
            const_zero = ir.Constant(ir.IntType(32), 0)
            const_one = ir.Constant(ir.IntType(32), 1)
            indices = []
            for arg in self.args:
                idx = arg.codegen(symbol_table, False)
                idx = arg.type.sub(symbol_table.llvm.builder, "idx_sub")(idx, const_one)
                indices.append(idx)
            gep_idx = None
            if lookup_result.type.is_function_param:
                gep_idx = ArrayIndex.get_func_ptr(symbol_table.llvm.builder, lookup_result.llvm_obj, indices)
            else:
                gep_idx = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, lookup_result.llvm_obj, indices)
            if lvalue:
                return gep_idx
            else:
                return symbol_table.llvm.builder.load(gep_idx, "gep_idx_load")

    @staticmethod
    def get_func_ptr(builder: ir.IRBuilder, arr_alloca: ir.AllocaInstr, indices: list):
        gep_idx = arr_alloca
        for idx in indices:
            gep_load = builder.load(gep_idx, "gep_load")
            gep_idx = builder.gep(gep_load, [idx], True, "gep_idx")
        return gep_idx

    @staticmethod
    def get_arr_ptr(builder: ir.IRBuilder, arr_alloca: ir.AllocaInstr | ir.GlobalVariable, indices: list):
        const_zero = ir.Constant(ir.IntType(32), 0)
        gep_idx = arr_alloca
        for idx in indices:
            gep_idx = builder.gep(gep_idx, [const_zero, idx], True, "gep_idx")
        return gep_idx


@dataclass
class ExitStatement(Statement):
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pass


@dataclass
class ExitFor(ExitStatement):
    name: Variable | None

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        var = None
        if len(attrs) != 0:
            varname = attrs[0]
            var = Variable(varname.pos, varname, varname.type)
        cexit = coords[0]
        return ExitFor(cexit.start, var)

    def relax(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.ForLoopBlock, accumulate=True)
        if not lookup_result:
            raise InappropriateExit(self.pos, self)
        if self.name:
            name_lookup_result = symbol_table.lookup(self.name.symbol(), by_origin=False)
            if not name_lookup_result:
                raise UndefinedSymbol(self.pos, self.name)
            for blocks in lookup_result:
                if blocks.block_obj.name == self.name.name:
                    return self
        return self

    def codegen(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.ForLoopBlock, accumulate=True)
        block = None
        for blocks in lookup_result:
            if blocks.block_obj.name == self.name.name:
                block = blocks
                break
        symbol_table.llvm.builder.branch(block.llvm.obj)


@dataclass
class ExitWhile(ExitStatement):

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cexit, cdo = coords
        return ExitWhile(cexit.start)

    def relax(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.WhileLoopBlock)
        if not lookup_result:
            raise InappropriateExit(self.pos, self)
        return self

    def codegen(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.WhileLoopBlock)
        lookup_result.llvm.builder.branch(lookup_result.llvm.obj)



@dataclass
class ExitSubroutine(ExitStatement):

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cexit, csub = coords
        return ExitSubroutine(cexit.start)

    def relax(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.SubroutineBlock)
        if not lookup_result:
            raise InappropriateExit(self.pos, self)
        return self

    def codegen(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.SubroutineBlock)
        if isinstance(lookup_result.llvm.obj, ir.Function):
            lookup_result.llvm.builder.branch(lookup_result.llvm.obj.basic_blocks[-1])


@dataclass
class ExitFunction(ExitStatement):

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cexit, cfunc = coords
        return ExitFunction(cexit.start)

    def relax(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.FunctionBlock)
        if not lookup_result:
            raise InappropriateExit(self.pos, self)
        return self

    def codegen(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup_block(SymbolTableBlockType.FunctionBlock)
        if isinstance(lookup_result.llvm.obj, ir.Function):
            lookup_result.llvm.builder.branch(lookup_result.llvm.obj.basic_blocks[-1])



@dataclass
class AssignStatement(Statement):
    pos: pe.Position
    variable: Variable | FuncCallOrArrayIndex
    expr: Expr

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        var, expr = attrs
        if isinstance(var, Varname):
            var = Variable(var.pos, var, var.type)
        cvar, ceq, cexpr = coords
        return AssignStatement(cvar.start, var, expr)

    def relax(self, symbol_table: SymbolTable):
        self.variable = self.variable.relax(symbol_table)
        global_lookup_result = symbol_table.lookup(self.variable.symbol(), by_type=False, by_origin=False)
        local_lookup_result = symbol_table.lookup(self.variable.symbol(), local=True, by_type=False, by_origin=False)
        if local_lookup_result:
            pass
        else:
            if global_lookup_result:
                pass
            else:
                if isinstance(self.variable, Variable):
                    result = VariableDecl(self.pos, self.variable, self.expr)
                    return result.relax(symbol_table)
                if not isinstance(self.variable, ArrayIndex):
                    raise UndefinedSymbol(self.pos, self.variable.name)
        self.expr = self.expr.relax(symbol_table, lvalue=False)
        if not self.expr.type.castable_to(self.variable.type):
            raise ConversionError(self.pos, self.expr.type, self.variable.type)
        return self

    def codegen(self, symbol_table: SymbolTable):
        const_zero = ir.Constant(ir.IntType(32), 0)
        variable = self.variable.codegen(symbol_table, True)
        expr_val = self.expr.codegen(symbol_table, False)
        if isinstance(variable, (ir.AllocaInstr, ir.GlobalVariable, ir.GEPInstr)):
            if isinstance(expr_val, ir.GlobalVariable) and isinstance(self.expr.type, StringT):
                expr_val = ArrayIndex.get_arr_ptr(symbol_table.llvm.builder, expr_val, [const_zero])
            if self.variable.type != self.expr.type:
                expr_val = self.expr.type.cast_to(self.variable.type, symbol_table.llvm.builder)(expr_val)
            if isinstance(self.variable.type, StringT) and isinstance(self.expr.type, StringT):
                if not self.expr.type.is_const:
                    str_copy_symbol = Program.string_copy_symbol()
                    lookup_result = symbol_table.lookup(str_copy_symbol, by_type=False)
                    if isinstance(symbol_table.llvm.builder, ir.IRBuilder):
                        expr_val = symbol_table.llvm.builder.call(lookup_result.llvm_obj, [expr_val],"str_copy_val")
            symbol_table.llvm.builder.store(expr_val, variable)


@dataclass
class ForLoop(Statement):
    variable: Variable
    cond_coord: pe.Position
    start: Expr
    start_coord: pe.Fragment
    end: Expr
    end_coord: pe.Fragment
    body: list[Statement]
    next: Variable
    next_coord: pe.Fragment

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, start, end, body, next_varname = attrs
        cfor_kw, cvar, cass, cstart, cto_kw, cend, cstmts, ckw_next, cnext_varname = coords
        var = Variable(varname.pos, varname, varname.type)
        next_variable = Variable(next_varname.pos, next_varname, next_varname.type)
        return ForLoop(var, cvar.start, start, cstart, end, cend, body, next_variable, cnext_varname)

    def relax(self, symbol_table: SymbolTable):
        lookup_result = symbol_table.lookup(self.variable.symbol(), local=True, by_type=False, by_origin=False)
        if lookup_result:
            raise RedefinitionError(self.cond_coord, self.variable.name, lookup_result.name)
        if not isinstance(self.variable.type, IntegralT):
            raise NotIntFor(self.cond_coord, self.variable.type)
        symbol_table.add(self.variable.symbol())
        if self.variable.name != self.next.name:
            raise UnexpectedNextFor(self.next_coord, self.variable.name, self.next.name)
        self.start = self.start.relax(symbol_table, lvalue=True)
        self.end = self.end.relax(symbol_table, lvalue=True)
        if not self.start.type.castable_to(self.variable.type):
            raise ConversionError(self.start_coord, self.start.type, self.variable.type)
        if not self.end.type.castable_to(self.variable.type):
            raise ConversionError(self.start_coord, self.end.type, self.variable.type)
        for_block = symbol_table.new_local(SymbolTableBlockType.ForLoopBlock, block_obj=self.variable)
        for idx, stmt in enumerate(self.body):
            self.body[idx] = stmt.relax(for_block)
        return self

    def codegen(self, symbol_table: SymbolTable):
        start = self.codegen_start(symbol_table)
        end = self.codegen_end(symbol_table)
        if isinstance(symbol_table.llvm.builder, ir.IRBuilder):
            if isinstance(symbol_table.llvm.builder.function, ir.Function):
                builder = symbol_table.llvm.builder
                func = builder.function
                idx_alloca = builder.alloca(self.variable.type.llvm_type(), 1)
                builder.store(start, idx_alloca)
                symbol_table.add(self.variable.symbol().assoc(idx_alloca))
                idx = func.basic_blocks.index(symbol_table.llvm.builder.block) + 1
                cond_block = func.insert_basic_block(idx,
                                                name=label_suffix(builder.block.name, ".for.cond"))
                cond_block_builder = ir.IRBuilder(cond_block)
                body_block = func.insert_basic_block(idx + 1,
                                                name=label_suffix(builder.block.name, ".for.body"))
                body_block_builder = ir.IRBuilder(body_block)
                inc_block = func.insert_basic_block(idx + 2,
                                               name=label_suffix(builder.block.name, ".for.inc"))
                inc_block_builder = ir.IRBuilder(inc_block)
                end_block = func.insert_basic_block(idx + 3,
                                               name=label_suffix(builder.block.name, ".for.end"))
                for_table = symbol_table.new_local(SymbolTableBlockType.ForLoopBlock,
                                                   block_obj=self.variable,
                                                   llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module,
                                                                                   body_block_builder,
                                                                                   end_block))
                builder.branch(cond_block)
                self.codegen_cond(cond_block_builder, idx_alloca, end, body_block, end_block)
                self.codegen_inc(inc_block_builder, idx_alloca, cond_block)

                for stmt in self.body:
                    stmt.codegen(for_table)

                if body_block_builder.block.terminator is None:
                    body_block_builder.branch(inc_block)

                builder.position_at_end(end_block)

    def codegen_start(self, symbol_table: SymbolTable):
        start = self.start.codegen(symbol_table)
        if self.start.type != self.variable.type:
            start = self.start.type.cast_to(self.variable.type, symbol_table.llvm.builder)(start)
        return start

    def codegen_end(self, symbol_table: SymbolTable):
        end = self.end.codegen(symbol_table)
        if self.end.type != self.variable.type:
            end = self.end.type.cast_to(self.variable.type, symbol_table.llvm.builder)(end)
        return end

    def codegen_cond(self, builder: ir.IRBuilder, idx_alloca, end_value, body_block, end_block):
        for_idx = builder.load(idx_alloca, "for.idx")
        for_cond = builder.icmp_signed("<=", for_idx, end_value)
        builder.cbranch(for_cond, body_block, end_block)

    def codegen_inc(self, builder: ir.IRBuilder, idx_alloca, block):
        inc_idx = builder.load(idx_alloca, "for.idx")
        inc_add = builder.add(inc_idx, ir.Constant(self.variable.type.llvm_type(), 1))
        builder.store(inc_add, idx_alloca)
        builder.branch(block)


@dataclass
class WhileLoop(Statement):
    pos: pe.Position
    condition: Expr | None
    body: list[Statement]
    type: WhileType

    def __init__(self, body, condition, loop_type):
        self.body = body
        self.condition = condition
        self.type = loop_type

    def relax(self, symbol_table: SymbolTable):
        if self.condition:
            self.condition = self.condition.relax(symbol_table, lvalue=False)
            if not isinstance(self.condition.type, IntegralT):
                raise WhileNotIntCondition(self.pos, self.condition.type)
        while_block = symbol_table.new_local(SymbolTableBlockType.WhileLoopBlock)
        for idx, stmt in enumerate(self.body):
            self.body[idx] = stmt.relax(while_block)
        return self

    def codegen(self, symbol_table: SymbolTable):
        if isinstance(symbol_table.llvm.builder, ir.IRBuilder):
            if isinstance(symbol_table.llvm.builder.function, ir.Function):
                builder = symbol_table.llvm.builder
                func = builder.function
                idx = func.basic_blocks.index(symbol_table.llvm.builder.block) + 1

                cond_block = func.insert_basic_block(idx,
                                                name=label_suffix(builder.block.name, ".for.cond"))
                cond_block_builder = ir.IRBuilder(cond_block)
                body_block = func.insert_basic_block(idx + 1,
                                                name=label_suffix(builder.block.name, ".for.body"))
                body_block_builder = ir.IRBuilder(body_block)
                end_block = func.insert_basic_block(idx + 2,
                                               name=label_suffix(builder.block.name, ".for.end"))
                while_table = symbol_table.new_local(SymbolTableBlockType.WhileLoopBlock,
                                                     llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module,
                                                                                     body_block_builder,
                                                                                     end_block))
                if self.type == WhileType.PreWhile or self.type == WhileType.PreUntil:
                    builder.branch(cond_block)
                else:
                    builder.branch(body_block)
                self.codegen_cond(symbol_table, cond_block_builder, body_block, end_block)

                for stmt in self.body:
                    stmt.codegen(while_table)

                if body_block_builder.block.terminator is None:
                    body_block_builder.branch(cond_block)

                builder.position_at_end(end_block)

    def codegen_cond(self, symbol_table: SymbolTable, builder: ir.IRBuilder, body_block, end_block):
        if self.condition:
            buffer = symbol_table.llvm.builder
            symbol_table.llvm.builder = builder
            cond_val = self.condition.codegen(symbol_table)
            symbol_table.llvm.builder = buffer
            const_val = ir.Constant(self.condition.type.llvm_type(), 0)
            op = "!=" if self.type == WhileType.PreWhile or self.type.PostWhile else "=="
            while_cond = self.condition.type.cmp(op, builder, "while.cond")(cond_val, const_val)
            builder.cbranch(while_cond, body_block, end_block)
        else:
            builder.branch(body_block)

    def __repr__(self):
        return f"While(type={self.type})"


@dataclass
class IfElseStatement(Statement):
    pos: pe.Position
    condition: Expr
    then_branch: list[Statement]
    else_branch: list[Statement]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cond, then_branch, else_branch = attrs
        cif, ccond, cthen_kw, cthen_br, celse_stmt, cend_kw, cif_kw = coords
        return IfElseStatement(ccond.start, cond, then_branch, else_branch)

    def relax(self, symbol_table: SymbolTable):
        self.condition = self.condition.relax(symbol_table)
        if not isinstance(self.condition.type, IntegralT):
            raise IfNotIntCondition(self. pos, self.condition.type)
        if_block = symbol_table.new_local(SymbolTableBlockType.IfThenBlock)
        for idx, stmt in enumerate(self.then_branch):
            self.then_branch[idx] = stmt.relax(if_block)
        else_block = symbol_table.new_local(SymbolTableBlockType.IfElseBlock)
        for idx, stmt in enumerate(self.else_branch):
            self.else_branch[idx] = stmt.relax(else_block)
        return self

    def codegen(self, symbol_table: SymbolTable):
        if len(self.else_branch) == 0:
            self.codegen_if_then(symbol_table)
        else:
            self.codegen_if_else(symbol_table)

    def codegen_if_else(self, symbol_table: SymbolTable):
        cond_val = self.condition.codegen(symbol_table)
        if isinstance(symbol_table.llvm.builder, ir.IRBuilder):
            if isinstance(symbol_table.llvm.builder.function, ir.Function):
                builder = symbol_table.llvm.builder
                func = builder.function
                idx = func.basic_blocks.index(symbol_table.llvm.builder.block) + 1

                if_then_block = func.insert_basic_block(idx,
                                                name=label_suffix(builder.block.name, ".if.then"))
                if_then_block_builder = ir.IRBuilder(if_then_block)
                if_else_block = func.insert_basic_block(idx + 1,
                                                name=label_suffix(builder.block.name, ".if.else"))
                if_else_block_builder = ir.IRBuilder(if_else_block)
                end_block = func.insert_basic_block(idx + 2,
                                               name=label_suffix(builder.block.name, ".if.end"))
                if_then_table = symbol_table.new_local(SymbolTableBlockType.IfThenBlock,
                                                       llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module,
                                                                                       if_then_block_builder,
                                                                                       end_block))
                if_else_table = symbol_table.new_local(SymbolTableBlockType.IfElseBlock,
                                                       llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module,
                                                                                       if_else_block_builder,
                                                                                       end_block))
                const_val = ir.Constant(self.condition.type.llvm_type(), 0)
                if_cond = self.condition.type.cmp("!=", builder, "if.cond")(cond_val, const_val)
                builder.cbranch(if_cond, if_then_block, if_else_block)

                for stmt in self.then_branch:
                    stmt.codegen(if_then_table)
                if if_then_block_builder.block.terminator is None:
                    if_then_block_builder.branch(end_block)

                for stmt in self.else_branch:
                    stmt.codegen(if_else_table)
                if if_else_block_builder.block.terminator is None:
                    if_else_block_builder.branch(end_block)

                builder.position_at_end(end_block)

    def codegen_if_then(self, symbol_table: SymbolTable):
        cond_val = self.condition.codegen(symbol_table)
        if isinstance(symbol_table.llvm.builder, ir.IRBuilder):
            if isinstance(symbol_table.llvm.builder.function, ir.Function):
                builder = symbol_table.llvm.builder
                func = builder.function
                idx = func.basic_blocks.index(symbol_table.llvm.builder.block) + 1
                if_then_block = func.insert_basic_block(idx,
                                                   name=label_suffix(builder.block.name, ".if.then"))
                if_then_block_builder = ir.IRBuilder(if_then_block)
                end_block = func.insert_basic_block(idx + 1,
                                               name=label_suffix(builder.block.name, ".if.end"))
                if_then_table = symbol_table.new_local(SymbolTableBlockType.IfThenBlock,
                                                       llvm_entry=SymbolTableLLVMEntry(symbol_table.llvm.module,
                                                                                       if_then_block_builder,
                                                                                       end_block))

                const_val = ir.Constant(self.condition.type.llvm_type(), 0)
                if_cond = self.condition.type.cmp("!=", builder, "if.cond")(cond_val, const_val)
                builder.cbranch(if_cond, if_then_block, end_block)

                for stmt in self.then_branch:
                    stmt.codegen(if_then_table)
                if if_then_block_builder.block.terminator is None:
                    if_then_block_builder.branch(end_block)

                builder.position_at_end(end_block)


@dataclass
class ImplicitTypeCast(Expr):
    pos: pe.Position
    type: Type
    expr: Expr

@dataclass
class UnaryOpExpr(Expr):
    pos: pe.Position
    op: str
    unary_expr: Expr

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        op, left = attrs
        cop, cleft = coords
        return UnaryOpExpr(cop.start, op, left)

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        self.unary_expr = self.unary_expr.relax(symbol_table, lvalue)
        if isinstance(self.unary_expr.type, ArrayT) or (not isinstance(self.unary_expr.type, NumericT)):
            raise UnaryBadType(self.pos, self.unary_expr.type, self.op)
        self.type = self.unary_expr.type
        return self

    def codegen(self, symbol_table: SymbolTable, lvalue: bool = True):
        expr_val = self.unary_expr.codegen(symbol_table, False)
        if self.op == '-':
            if isinstance(self.unary_expr.type, NumericT):
                expr_val = self.unary_expr.type.neg(symbol_table.llvm.builder, "expr.val.neg")(expr_val)
        return expr_val



@dataclass
class BinOpExpr(Expr):
    pos: pe.Position
    left: Expr
    op: str
    right: Expr

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        left, op, right = attrs
        cleft, cop, cright = coords
        return BinOpExpr(cleft.start, left, op, right)

    def relax(self, symbol_table: SymbolTable, lvalue=True):
        self.left = self.left.relax(symbol_table, lvalue)
        self.right = self.right.relax(symbol_table, lvalue)
        if isinstance(self.left.type, NumericT) and isinstance(self.right.type, NumericT):
            result_type = None
            if self.op in ('+', '-', '*'):
                if self.left.type.castable_to(self.right.type):
                    result_type = self.right.type
                elif self.right.type.castable_to(self.left.type):
                    result_type = self.left.type
            elif self.op == '/':
                result_type = DoubleT()
            elif self.op in ('>', '<', '>=', '<=', '=', '<>'):
                result_type = BoolT()
            else:
                raise UndefinedBinOperType(self.pos, self.left.type, self.op, self.right.type)
            if not result_type:
                raise BinBadType(self.pos, self.left.type, self.op, self.right.type)
            self.type = result_type
        elif isinstance(self.left.type, StringT) and isinstance(self.right.type, StringT):
            if self.op != '+':
                raise BinBadType(self.pos, self.left.type, self.op, self.right.type)
            self.type = StringT()
        else:
            raise BinBadType(self.pos, self.left.type, self.op, self.right.type)
        return self

    def codegen(self, symbol_table: SymbolTable, lvalue: bool = True):
        lhs_val = self.left.codegen(symbol_table, False)
        rhs_val = self.right.codegen(symbol_table, False)
        result_val = None
        if self.type == StringT():
            str_concat_symbol = Program.string_concat_symbol()
            lookup_result = symbol_table.lookup(str_concat_symbol, by_type=False)
            if isinstance(symbol_table.llvm.builder, ir.IRBuilder):
                result_val = symbol_table.llvm.builder.call(lookup_result.llvm_obj, [lhs_val, rhs_val], "str_concat_val")
        elif isinstance(self.left.type, NumericT) and isinstance(self.right.type, NumericT):
            if self.op in ('>', '<', '>=', '<=', '=', '<>'):
                result_val = self.type.cmp(self.op, symbol_table.llvm.builder, "bin_cmp_val")(lhs_val, rhs_val)
            else:
                if self.left.type != self.type:
                    lhs_val = self.left.type.cast_to(self.type, symbol_table.llvm.builder)(lhs_val)
                if self.right.type != self.type:
                    rhs_val = self.right.type.cast_to(self.type, symbol_table.llvm.builder)(rhs_val)
                if self.op == "+":
                    result_val = self.type.add(symbol_table.llvm.builder, "bin_add_val")(lhs_val, rhs_val)
                elif self.op == "-":
                    result_val = self.type.sub(symbol_table.llvm.builder, "bin_sub_val")(lhs_val, rhs_val)
                elif self.op == "*":
                    result_val = self.type.mul(symbol_table.llvm.builder, "bin_mul_val")(lhs_val, rhs_val)
                elif self.op == "/":
                    result_val = self.type.div(symbol_table.llvm.builder, "bin_div_val")(lhs_val, rhs_val)
        return result_val


@dataclass
class Program:
    decls: list[SubroutineDecl | FunctionDecl | SubroutineDef | FunctionDef | VariableDecl]
    symbol_table: SymbolTable

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        global_decls = attrs[0]
        declarations = Program.standart_library() + global_decls
        program = Program(declarations, SymbolTable(block_type=SymbolTableBlockType.GlobalBlock))
        program = program.relax()
        return program

    def relax(self):
        for idx, decl in enumerate(self.decls):
            self.decls[idx] = decl.relax(self.symbol_table)
        return self

    def codegen(self, module_name=None):
        program_module = ir.Module(name=module_name if module_name else __file__)
        program_module.triple = binding.get_default_triple()
        program_module.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8  :16:32:64-S128"
        global_constr = GlobalConstructor(program_module, "variable_decl_constructor")
        global_constr_sub = ir.Function(program_module, ir.FunctionType(ir.VoidType(), []), "variable_decl_constructor")
        global_builder = ir.IRBuilder(global_constr_sub.append_basic_block("entry"))
        global_builder.ret_void()
        global_constr_symbol = Program.global_constructor_symbol().assoc(global_constr_sub)
        self.symbol_table = SymbolTable(block_type=SymbolTableBlockType.GlobalBlock,
                                        llvm_entry=SymbolTableLLVMEntry(program_module))
        self.symbol_table.add(global_constr_symbol)

        for decl in self.decls:
            decl.codegen(self.symbol_table)
        return program_module

    @staticmethod
    def standart_library() -> list:
        standart_decls = []
        types = [IntegerT(), LongT(), FloatT(), DoubleT(), StringT()]

        for tp in types:
            symbol = Program.print_symbol(tp)
            print_arg = [Variable(pe.Position(), Varname(pe.Position(), "val", tp), tp)]
            print_proto = SubroutineProto(pe.Position(), symbol.name, print_arg, symbol.type)
            print_sub = SubroutineDecl(pe.Position(), print_proto, True)
            standart_decls.append(print_sub)

        default_pos = pe.Position(-1, -1, -1)
        len_arg = [Variable(default_pos, Varname(default_pos, "arr", Type()), ArrayT(Type(), [], True))]
        len_proto = FunctionProto(default_pos, Varname(default_pos, "Len", IntegerT()), len_arg,
                                  ProcedureT(IntegerT(), [arg.type for arg in len_arg]))
        len_func = FunctionDecl(default_pos, len_proto, True)
        standart_decls.append(len_func)

        default_pos = pe.Position(-1, -1, -1)
        str_concat_arg = [Variable(default_pos, Varname(default_pos, "lhs", StringT()), StringT()),
                          Variable(default_pos, Varname(default_pos, "rhs", StringT()), StringT())]
        str_concat_proto = FunctionProto(default_pos, Varname(default_pos, "StringConcat", StringT()), str_concat_arg,
                                  ProcedureT(StringT(), [arg.type for arg in str_concat_arg]))
        str_concat_func = FunctionDecl(default_pos, str_concat_proto, True)
        standart_decls.append(str_concat_func)

        str_copy_arg = [Variable(default_pos, Varname(default_pos, "lhs", StringT()), StringT())]
        str_copy_proto = FunctionProto(default_pos, Varname(default_pos, "StringCopy", StringT()), str_copy_arg,
                                         ProcedureT(StringT(), [arg.type for arg in str_copy_arg]))
        str_copy_func = FunctionDecl(default_pos, str_copy_proto, True)
        standart_decls.append(str_copy_func)

        return standart_decls

    @staticmethod
    def print_symbol(tp: Type):
        if isinstance(tp, NumericT) or isinstance(tp, StringT):
            print_varname = Varname(pe.Position(), f"Print{tp.mangle_suff}", VoidT())
            return Symbol(print_varname, ProcedureT(VoidT(), [tp]), True)
        else:
            raise RuntimeError("Bad print type")

    @staticmethod
    def len_symbol():
        len_arg_type = ArrayT(Type(), [], True)
        len_varname = Varname(pe.Position(), "Len", IntegerT())
        return Symbol(len_varname, ProcedureT(VoidT(), [len_arg_type]), True)

    @staticmethod
    def global_constructor_symbol():
        return Symbol(Varname(None, "variable_decl_constructor", VoidT()), ProcedureT(VoidT(), []))

    @staticmethod
    def string_concat_symbol():
        return Symbol(Varname(pe.Position(), "StringConcat", StringT()), ProcedureT(StringT(), [StringT(), StringT()]), True)

    @staticmethod
    def string_copy_symbol():
        return Symbol(Varname(pe.Position(), "StringCopy", StringT()), ProcedureT(StringT(), [StringT()]), True)