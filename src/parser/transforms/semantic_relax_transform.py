from src.parser import basic_ast
from src.parser.analyzers.is_const_expr import IsConstExpr
from src.parser.basic_ast_generator import ImplicitCastAstGenerator
from src.parser.basic_types import *
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import SymbolTable, Symbol, STLookupStrategy, STLookupScope, STBlockType
from src.parser.errors import *


class SemanticRelaxTransform:
    @staticmethod
    def transform(node, st: SymbolTable = None, standart_library = None):
        match type(node):
            case t if t is basic_ast.Program:
                return SRProgram.transform(node, standart_library)
            case t if t is basic_ast.FunctionDecl:
                return SRFunctionDecl.transform(node, st)
            case t if t is basic_ast.FunctionDef:
                return SRFunctionDef.transform(node, st)
            case t if t is basic_ast.FunctionProto:
                return SRFunctionProto.transform(node, st)
            case t if t is basic_ast.SubroutineDecl:
                return SRFunctionDecl.transform(node, st)
            case t if t is basic_ast.SubroutineDef:
                return SRFunctionDef.transform(node, st, _add_func_ret=False)
            case t if t is basic_ast.SubroutineProto:
                return SRFunctionProto.transform(node, st)
            case t if t is basic_ast.InitializerList:
                return SRInitializerList.transform(node, st)
            case t if t is basic_ast.VariableDecl:
                return SRVariableDecl.transform(node, st)
            case t if t is basic_ast.Array:
                return SRArray.transform(node, st)
            case t if t is basic_ast.ArrayReference:
                return SRArray.transform(node, st)
            case t if t is basic_ast.Variable:
                return SRVariable.transform(node, st)
            case t if t is basic_ast.FuncCallOrArrayIndex:
                return SRFuncCallOrArrayIndex.transform(node, st)
            case t if t is basic_ast.PrintCall:
                return SRPrintCall.transform(node, st)
            case t if t is basic_ast.FuncCall:
                return SRFuncCall.transform(node, st)
            case t if t is basic_ast.ArrayIndex:
                return SRArrayIndex.transform(node, st)
        return None


class SRProgram:
    @staticmethod
    def transform(node: basic_ast.Program, std_library: basic_ast.Program):
        table = SymbolTable()
        result = node
        result.decls = std_library.decls + result.decls
        for idx, declaration in enumerate(result.decls):
            result.decls[idx] = SemanticRelaxTransform.transform(declaration, st=table)
        return result, table


class SRFunctionDef:
    @staticmethod
    def transform(node: basic_ast.FunctionDef, st: SymbolTable = None, _add_func_ret=True):
        result = node
        symbol = SymbolFactory.create(result)
        lookup_result = st.qnl(STLookupStrategy(symbol, STLookupScope.Global))
        if lookup_result.empty():
            st.add(symbol)
        elif lookup_result.length() == 1 and lookup_result.first().declaration:
            symb = st[lookup_result.first().path()]
            symb.declaration = False
            st[lookup_result.first().path()] = symb
        else:
            raise RedefinitionError(result.pos, result.proto.name, lookup_result.first().name.pos)
        result.proto = SemanticRelaxTransform.transform(result.proto, st=st)
        local_function_scope = st.new_table(STBlockType.FunctionBlock)
        if _add_func_ret:
            func_ret_variable = basic_ast.Variable(result.proto.name.pos, result.proto.name, result.proto.type.retT)
            local_function_scope.add(SymbolFactory.create(func_ret_variable))
        for var in result.proto.args:
            local_function_scope.add(SymbolFactory.create(var))
        for idx, stmt in enumerate(result.body):
            result.body[idx] = SemanticRelaxTransform.transform(result.body[idx], st=local_function_scope)
        return result

class SRFunctionDecl:
    @staticmethod
    def transform(node: basic_ast.FunctionDecl, st: SymbolTable = None):
        result = node
        symbol = SymbolFactory.create(result)
        lookup_result = st.qnl(STLookupStrategy(symbol, STLookupScope.Local))
        if not lookup_result.empty() and lookup_result.first().declaration:
            raise RedefinitionError(result.pos, result.proto.name, lookup_result.first().name.pos)
        elif lookup_result.empty():
            st.add(symbol)
        result.proto = SemanticRelaxTransform.transform(result.proto, st)
        return result

class SRFunctionProto:
    @staticmethod
    def transform(node: basic_ast.FunctionProto, st: SymbolTable = None):
        result = node
        names = [result.name]
        for idx, var in enumerate(result.args):
            if var.name in names:
                raise RedefinitionError(var.pos, var.name, names[names.index(var.name)].pos)
        return result

class SRInitializerList:
    @staticmethod
    def transform(node: basic_ast.InitializerList, st: SymbolTable = None):
        result = node
        if not all(type(result.values[0]) == type(value) for value in result.values):
            for value in result.values:
                if type(result.values[0]) != type(value):
                    raise InappropriateInitializerList(result.pos, type(result.values[0]), type(value))
        for idx, value in enumerate(result.values):
            result.values[idx] = SemanticRelaxTransform.transform(value, st)
        if isinstance(result.values[0], basic_ast.InitializerList):
            if not all(SRInitializerList.dimensions(result.values[0]) == SRInitializerList.dimensions(value) for value in result.values):
                for value in result.values:
                    if SRInitializerList.dimensions(result.values[0]) != SRInitializerList.dimensions(value):
                        raise InappropriateInitializerList(result.pos, SRInitializerList.dimensions(result.values[0]), SRInitializerList.dimensions(value))
        return result

    @staticmethod
    def dimensions(node: basic_ast.InitializerList):
        if len(node.values) == 0:
            return [0]
        if isinstance(node.values[0], basic_ast.InitializerList):
            return [len(node.values)] + SRInitializerList.dimensions(node.values[0])
        else:
            return [len(node.values)]

    @staticmethod
    def common_type(node: basic_ast.InitializerList):
        if len(node.values) == 0:
            return None
        if isinstance(node.values[0], basic_ast.InitializerList):
            return common_type(types=[SRInitializerList.common_type(value) for value in node.values])
        else:
            return common_type(types=[value.type for value in node.values])

class SRVariableDecl:
    @staticmethod
    def transform(node: basic_ast.VariableDecl, st: SymbolTable = None):
        result = node
        symbol = SymbolFactory.create(node.variable)
        if st is not None and not (lookup_result := st.qnl(STLookupStrategy(symbol, STLookupScope.Local))).empty():
            raise RedefinitionError(node.pos, node.variable.name, lookup_result.first().name.pos)
        if node.init_value is not None:
            return SRVariableDecl.__transfrom_init_value(node, st)
        if isinstance(node.variable.type, basic_ast.Array):
            if isinstance(node.variable.type.size[0], int):
                raise InitializationUndefinedLengthError(node.pos, node.variable.size)
            for idx, sz in enumerate(node.variable.size):
                if not (isinstance(sz, basic_ast.ConstExpr) and sz.type == IntegralT()):
                    raise InitializationUndefinedLengthError(node.pos, node.variable.size)
            result.variable = SemanticRelaxTransform.transform(result.variable, st)
        st.add(symbol)
        return result

    @staticmethod
    def __transfrom_init_value(node: basic_ast.VariableDecl, st: SymbolTable = None):
        result = node
        result.init_value = SemanticRelaxTransform.transform(result.init_value, st)
        if isinstance(result.variable, basic_ast.Array):
            if not isinstance(result.init_value, basic_ast.InitializerList):
                raise InappropriateInitializerList(result.pos, f"InitializerList{{{result.variable.type}}}", result.init_value)
            implicit_type = common_type(result.variable.type, SRInitializerList.common_type(result.init_value))
            if implicit_type is None or implicit_type != result.variable.type:
                raise ConversionError(result.pos, result.init_value.type, result.variable.type.value_type)
            elif implicit_type == result.variable.type:
                result = ImplicitCastAstGenerator.generate(result, implicit_type)
            result.variable = SemanticRelaxTransform.transform(result.variable, st)
            result.variable.type.size = SRVariableDecl.__get_array_size(result)
            result.variable.size = [basic_ast.ConstExpr(result.variable.pos, value, IntegerT()) for value in result.variable.type.size]
        else:
            init_type = SRInitializerList.common_type(result.init_value) if isinstance(result.init_value, basic_ast.InitializerList) else result.init_value.type
            implicit_type = common_type(result.variable.type, init_type)
            if implicit_type is None or implicit_type != result.variable.type:
                raise ConversionError(result.pos, result.init_value.type, result.variable.type)
            elif implicit_type == result.variable.type:
                result = ImplicitCastAstGenerator.generate(result, implicit_type)
            if isinstance(result.init_value, basic_ast.InitializerList):
                list_size = SRInitializerList.dimensions(result.init_value)
                expr_size = [basic_ast.ConstExpr(result.variable.pos, value, IntegerT()) for value in list_size]
                result.variable = basic_ast.Array(result.variable.pos, result.variable.name, ArrayT(result.variable.type, list_size), expr_size)
        st.add(SymbolFactory.create(result.variable))
        return result

    @staticmethod
    def __get_array_size(node: basic_ast.VariableDecl):
        expected_size, given_size = node.variable.size, SRInitializerList.dimensions(node.init_value)
        if len(expected_size) != len(given_size):
            raise InitializationLengthMismatchError(node.pos, expected_size, given_size)
        for sz in expected_size:
            if not IsConstExpr(sz):
                raise InitializationNonConstSize(sz.pos, sz)
            if sz.value <= 0:
                raise InitializationNegativeSize(sz.pos, sz)
        result = [sz.value for sz in expected_size]
        for i in range(len(expected_size)):
            if expected_size[i] == 0 and given_size[i] == 0:
                raise InitializationUndefinedLengthError(node.pos, expected_size)
            elif expected_size[i] != 0 and given_size[i] != 0:
                if result[i] != given_size[i]:
                    raise InitializationLengthMismatchError(node.pos, expected_size, given_size)
            result[i] = max(result[i], given_size[i])
        return result


class SRVariable:
    @staticmethod
    def transform(node: basic_ast.Variable, st: SymbolTable):
        symbol = SymbolFactory.create(node)
        lookup_result = st.qnl(STLookupStrategy(symbol, STLookupScope.Global))
        name_lookup_result = st.unql(STLookupStrategy(symbol, STLookupScope.Global))
        if name_lookup_result.empty():
            raise UndefinedSymbol(node.pos, node.name)
        if lookup_result.empty():
            node.type = name_lookup_result.first().type
            if isinstance(node.type, ArrayT):
                result = basic_ast.ArrayReference(node.pos, node.name, node.type)
                SemanticRelaxTransform.transform(result, st)
                return result
        return node

class SRArray:
    @staticmethod
    def transform(node: basic_ast.Array, st: SymbolTable = None):
        result = node
        if isinstance(result.type.size[0], int):
            return result
        for idx, expr in enumerate(result.size):
            result.size[idx] = SemanticRelaxTransform.transform(expr, st)
            if not isinstance(result.size[idx].type, IntegralT):
                raise ArrayNotIntInit(result.pos, result.size[idx].type)
        return result

class SRFuncCallOrArrayIndex:
    @staticmethod
    def transform(node: basic_ast.FuncCallOrArrayIndex, st: SymbolTable):
        result = node
        lookup_result = st.unql(STLookupStrategy(SymbolFactory.create(node.name), STLookupScope.Global))
        if lookup_result.empty():
            raise UndefinedSymbol(node.pos, node.name)
        if isinstance(lookup_result.first().type, ArrayT):
            result = SemanticRelaxTransform.transform(basic_ast.ArrayIndex(node.pos, node.name, node.args, node.name.type), st)
        elif isinstance(lookup_result.first().type, ProcedureT):
            result = SemanticRelaxTransform.transform(basic_ast.FuncCall(node.pos, node.name, node.args, node.name.type), st)
        return result

class SRPrintCall:
    @staticmethod
    def transform(node: basic_ast.PrintCall, st: SymbolTable):
        result = node
        for idx, arg in enumerate(node.args):
            result.args[idx] = SemanticRelaxTransform.transform(arg, st)
            if not isinstance(result.args[idx].type, (NumericT, StringT)):
                raise UndefinedFunction(result.pos, result.name, ProcedureT(VoidT(), [arg.type]))
        return result

class SRFuncCall:
    @staticmethod
    def transform(node: basic_ast.FuncCall, st: SymbolTable):
        result = node
        for idx, arg in enumerate(node.args):
            result.args[idx] = SemanticRelaxTransform.transform(arg, st)
        func_call_symbol = SymbolFactory.create(node)
        if not st.qnl(STLookupStrategy(func_call_symbol, STLookupScope.Global)).empty():
            return result
        if not (lookup_result := st.unql(STLookupStrategy(func_call_symbol, STLookupScope.Global))).empty():
            for func in lookup_result:
                if common_type(func.type, func_call_symbol.type) == func.type:
                    return ImplicitCastAstGenerator.generate(result, func.type)
            raise UndefinedFunction(result.pos, result.name, func_call_symbol.type)
        raise UndefinedSymbol(node.pos, node.name)

class SRArrayIndex:
    @staticmethod
    def transform(node: basic_ast.ArrayIndex, st: SymbolTable):
        result = node
        for idx, arg in enumerate(node.args):
            result.args[idx] = SemanticRelaxTransform.transform(arg, st)
            if not isinstance(result.args[idx].type, IntegralT):
                raise ArrayNotIntIndexing(result.pos, result.args[idx].type)
        symbol = SymbolFactory.create(node)
        if not (lookup_result := st.unql(STLookupStrategy(symbol, STLookupScope.Global))).empty():
            if len(result.args) != len(lookup_result.first().type.size):
                if len(result.args) > len(lookup_result.first().type.size):
                    raise ArrayIndexingDimensionMismatchError(result.pos, len(lookup_result.first().type.size), len(result.args))
            result.type = ArrayT(result.name.type, lookup_result.first().type.size[len(result.args):len(lookup_result.first().type.size)])
        raise UndefinedSymbol(node.pos, node.name)