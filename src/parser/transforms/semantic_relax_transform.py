from _ast import Continue

from src.parser import basic_ast
from src.parser.analyzers.is_const_expr import is_const_expr
from src.parser.basic_ast_generator import ImplicitCastAstGenerator
from src.parser.basic_types import *
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import SymbolTable, Symbol, STLookupStrategy, STLookupScope, STBlockType
from src.parser.errors import *
from src.optimizer.transforms.constant_folding import ConstantFoldingTransform


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
                return SRArrayReference.transform(node, st)
            case t if t is basic_ast.Variable:
                return SRVariable.transform(node, st)
            case t if t is basic_ast.VariableReference:
                return node
            case t if t is basic_ast.FuncCallOrArrayIndex:
                return SRFuncCallOrArrayIndex.transform(node, st)
            case t if t is basic_ast.PrintCall:
                return SRPrintCall.transform(node, st)
            case t if t is basic_ast.LenCall:
                return SRLenCall.transform(node, st)
            case t if t is basic_ast.FuncCall:
                return SRFuncCall.transform(node, st)
            case t if t is basic_ast.ArrayIndex:
                return SRArrayIndex.transform(node, st)
            case t if t is basic_ast.ExitFor:
                return SRExitFor.transform(node, st)
            case t if t is basic_ast.ExitWhile:
                return SRExit.transform(node, st)
            case t if t is basic_ast.ExitFunction:
                return SRExit.transform(node, st)
            case t if t is basic_ast.ExitSubroutine:
                return SRExit.transform(node, st)
            case t if t is basic_ast.AssignStatement:
                return SRAssignStatement.transform(node, st)
            case t if t is basic_ast.ForLoop:
                return SRForLoop.transform(node, st)
            case t if t is basic_ast.WhileLoop:
                return SRWhileLoop.transform(node, st)
            case t if t is basic_ast.IfElseStatement:
                return SRIfStatement.transform(node, st)
            case t if t is basic_ast.ImplicitTypeCast:
                return SRImplicitTypeCast.transform(node, st)
            case t if t is basic_ast.UnaryOpExpr:
                return SRUnaryOpExpr.transform(node, st)
            case t if t is basic_ast.BinOpExpr:
                return SRBinaryOpExpr.transform(node, st)
            case t if t is basic_ast.ConstExpr:
                return SRConstExpr.transform(node, st)
        return None


class SRProgram:
    @staticmethod
    def transform(node: basic_ast.Program, std_library: basic_ast.Program):
        table = SymbolTable()
        result = node
        result.decls = std_library.decls + result.decls
        for idx, declaration in enumerate(result.decls):
            result.decls[idx] = SemanticRelaxTransform.transform(declaration, st=table)
        result.decls = list(filter(lambda d: d is not None, result.decls))
        return result, table


class SRFunctionDef:
    @staticmethod
    def transform(node: basic_ast.FunctionDef, st: SymbolTable, _add_func_ret=True):
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
            raise RedefinitionError(result.pos, result.proto.name, lookup_result.first().loc)
        result.proto = SemanticRelaxTransform.transform(result.proto, st=st)
        local_function_scope = st.new_table(STBlockType.FunctionBlock)
        if _add_func_ret:
            func_ret_variable = basic_ast.Variable(result.proto.name.pos, result.proto.name, result.proto.type.return_type)
            local_function_scope.add(SymbolFactory.create(func_ret_variable))
        for var in result.proto.args:
            local_function_scope.add(SymbolFactory.create(var))
        for idx, stmt in enumerate(result.body):
            result.body[idx] = SemanticRelaxTransform.transform(result.body[idx], st=local_function_scope)
        return result

class SRFunctionDecl:
    @staticmethod
    def transform(node: basic_ast.FunctionDecl, st: SymbolTable):
        result = node
        symbol = SymbolFactory.create(result)
        lookup_result = st.qnl(STLookupStrategy(symbol, STLookupScope.Local))
        if not lookup_result.empty() and lookup_result.first().declaration:
            raise RedefinitionError(result.pos, result.proto.name, lookup_result.first().name.pos)
        elif lookup_result.empty():
            st.add(symbol)
        result.proto = SemanticRelaxTransform.transform(result.proto, st)
        if result.proto.name.name == 'Len' and result.proto.name.type == IntegerT():
            return None
        return result

class SRFunctionProto:
    @staticmethod
    def transform(node: basic_ast.FunctionProto, st: SymbolTable):
        result = node
        names = [result.name]
        for idx, var in enumerate(result.args):
            if var.name in names:
                raise RedefinitionError(var.pos, var.name, names[names.index(var.name)].pos)
        return result

class SRInitializerList:
    @staticmethod
    def transform(node: basic_ast.InitializerList, st: SymbolTable):
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
        result.type = ArrayT(SRInitializerList.common_type(result), SRInitializerList.dimensions(result))
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
    def transform(node: basic_ast.VariableDecl, st: SymbolTable):
        result = node
        symbol = SymbolFactory.create(node.variable)
        if st is not None and not (lookup_result := st.bnl(STLookupStrategy(symbol, STLookupScope.Local))).empty():
            raise RedefinitionError(node.pos, node.variable.name, lookup_result.first().name.pos)
        if node.init_value is not None:
            return SRVariableDecl.__transform_init_value(node, st)
        if isinstance(node.variable, basic_ast.Array):
            if isinstance(node.variable.type.size[0], int):
                raise InitializationUndefinedLengthError(node.pos, node.variable.size)
            result.variable = SemanticRelaxTransform.transform(result.variable, st)
            for idx, sz in enumerate(node.variable.size):
                if not (is_const_expr(sz) and isinstance(sz.type, IntegralT)):
                    raise InitializationUndefinedLengthError(node.pos, node.variable.size)
            result = ConstantFoldingTransform.transform(result)
            result.variable.type.size = [int(sz.value) for sz in result.variable.size]
        st.add(symbol)
        return result

    @staticmethod
    def __transform_init_value(node: basic_ast.VariableDecl, st: SymbolTable):
        result = node
        result.init_value = SemanticRelaxTransform.transform(result.init_value, st)
        if isinstance(result.variable, basic_ast.Array):
            if not isinstance(result.init_value, basic_ast.InitializerList):
                raise InappropriateInitializerList(result.pos, f"InitializerList{{{result.variable.type}}}", result.init_value)
            implicit_type = common_type(result.variable.type.value_type, SRInitializerList.common_type(result.init_value))
            if implicit_type is None or implicit_type != result.variable.type.value_type:
                raise ConversionError(result.pos, result.init_value.type, result.variable.type.value_type)
            elif implicit_type == result.variable.type.value_type:
                result = ImplicitCastAstGenerator.generate(result, implicit_type)
            result.variable = SemanticRelaxTransform.transform(result.variable, st)
            result.variable.type.size = SRVariableDecl.__resolve_array_size(result)
            result.variable.size = [basic_ast.ConstExpr(result.variable.pos, value, IntegerT()) for value in result.variable.type.size]
            result.init_value = SemanticRelaxTransform.transform(result.init_value, st)
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
                result.init_value = SemanticRelaxTransform.transform(result.init_value, st)
        st.add(SymbolFactory.create(result.variable))
        return result

    @staticmethod
    def __resolve_array_size(node: basic_ast.VariableDecl):
        expected_size, given_size = node.variable.size, SRInitializerList.dimensions(node.init_value)
        if len(expected_size) != len(given_size):
            raise InitializationLengthMismatchError(node.pos, expected_size, given_size)
        for sz in expected_size:
            if not is_const_expr(sz):
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
        result = node
        symbol = SymbolFactory.create(node)
        lookup_result = st.qnl(STLookupStrategy(symbol, STLookupScope.Global))
        name_lookup_result = st.unql(STLookupStrategy(symbol, STLookupScope.Global))
        if name_lookup_result.empty():
            raise UndefinedSymbol(node.pos, node.name)
        found_symbol = name_lookup_result.first() if lookup_result.empty() else lookup_result.first()
        match type(found_symbol.type):
            case t if t is PointerT and type(found_symbol.type.type) is ArrayT:
                node_size = found_symbol.type.type.size
                result.type = found_symbol.type
                result = basic_ast.ArrayReference(node.pos, node.name, result.type, node_size)
                result = SemanticRelaxTransform.transform(result, st)
            case t if t is ArrayT:
                result = basic_ast.ArrayReference(node.pos, node.name, PointerT(found_symbol.type), found_symbol.type.size)
                result = SemanticRelaxTransform.transform(result, st)
            case t if t is StringT:
                result = basic_ast.Variable(node.pos, node.name, PointerT(node.type))
                result = SemanticRelaxTransform.transform(result, st)
        return result

class SRArray:
    @staticmethod
    def transform(node: basic_ast.Array, st: SymbolTable):
        result = node
        if isinstance(result.type.size[0], int):
            return result
        for idx, expr in enumerate(result.size):
            result.size[idx] = SemanticRelaxTransform.transform(expr, st)
            if not isinstance(result.size[idx].type, IntegralT):
                raise ArrayNotIntInit(result.pos, result.size[idx].type)
        return result

class SRArrayReference:
    @staticmethod
    def transform(node: basic_ast.ArrayReference, st: SymbolTable):
        result = node
        if isinstance(result.type.type.size[0], int):
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
        lookup_result = st.bnl(STLookupStrategy(SymbolFactory.create(node), STLookupScope.Global))
        if lookup_result.empty():
            raise UndefinedSymbol(node.pos, node.name)
        if isinstance(lookup_result.first().type, (ArrayT, PointerT)):
            result = SemanticRelaxTransform.transform(basic_ast.ArrayIndex(node.pos, node.name, node.args, node.name.type), st)
        elif isinstance(lookup_result.first().type, ProcedureT):
            result = SemanticRelaxTransform.transform(basic_ast.FuncCall(node.pos, node.name, node.args, node.name.type), st)
        else:
            raise UndefinedSymbol(node.pos, node.name)
        return result

class SRPrintCall:
    @staticmethod
    def transform(node: basic_ast.PrintCall, st: SymbolTable):
        result = node
        for idx, arg in enumerate(node.args):
            result.args[idx] = SemanticRelaxTransform.transform(arg, st)
            if not isinstance(result.args[idx].type, (NumericT, PointerT)):
                raise UndefinedFunction(result.pos, result.name, ProcedureT(VoidT(), [arg.type]))
        return result

class SRLenCall:
    @staticmethod
    def transform(node: basic_ast.LenCall, st: SymbolTable):
        result = node
        result.array = SemanticRelaxTransform.transform(result.array, st)
        if not isinstance(result.array.type, (ArrayT, PointerT)):
            raise UndefinedFunction(result.pos, 'Len', ProcedureT(IntegerT(), [result.array.type]))
        return result

class SRFuncCall:
    @staticmethod
    def transform(node: basic_ast.FuncCall, st: SymbolTable):
        result = node
        for idx, arg in enumerate(node.args):
            result.args[idx] = SemanticRelaxTransform.transform(arg, st)
        func_call_symbol = SymbolFactory.create(node)
        if not (lookup_result := st.qnl(STLookupStrategy(func_call_symbol, STLookupScope.Global))).empty():
            if lookup_result.first().declaration and lookup_result.first().name == 'Len':
                return SemanticRelaxTransform.transform(basic_ast.LenCall(result.pos, result.args[0], IntegerT()), st)
            return result
        if not (lookup_result := st.unql(STLookupStrategy(func_call_symbol, STLookupScope.Global))).empty():
            for func in lookup_result:
                if common_type(func.type, func_call_symbol.type) == func.type:
                    return ImplicitCastAstGenerator.generate(result, func.type)
            raise UndefinedFunction(result.pos, result.name.name, func_call_symbol.type)
        raise UndefinedSymbol(node.pos, node.name)

class SRArrayIndex:
    @staticmethod
    def transform(node: basic_ast.ArrayIndex, st: SymbolTable):
        result = node
        for idx, arg in enumerate(node.args):
            result.args[idx] = SemanticRelaxTransform.transform(arg, st)
            if not isinstance(result.args[idx].type, IntegralT):
                raise ArrayNotIntIndexing(result.pos, result.args[idx].type)
            if is_const_expr(result.args[idx]) and (array_idx := ConstantFoldingTransform.transform(result.args[idx])).value < 1:
                raise ArrayInvalidIndex(result.pos, array_idx.value)
        symbol = SymbolFactory.create(node)
        if (lookup_result := st.unql(STLookupStrategy(symbol, STLookupScope.Global))).empty():
            raise UndefinedSymbol(node.pos, node.name)
        symbol_type = lookup_result.first().type
        symbol_shape = symbol_type.size if isinstance(symbol_type, ArrayT) else symbol_type.type.size
        if len(result.args) != len(symbol_shape):
            if len(result.args) > len(symbol_shape):
                raise ArrayIndexingDimensionMismatchError(result.pos, len(symbol_shape),len(result.args))
            result.type = PointerT(ArrayT(result.name.type, symbol_shape[len(result.args):len(symbol_shape)]))
        return result

class SRExitFor:
    @staticmethod
    def transform(node: basic_ast.ExitFor, st: SymbolTable):
        result = node
        if (blocks := st.bl(STBlockType.ForLoopBlock)).empty():
            raise InappropriateExit(node.pos, node)
        if node.name is not None and st.qnl(STLookupStrategy(SymbolFactory.create(node), STLookupScope.Global)).empty():
            raise UndefinedSymbol(node.pos, node.name)
        if node.name is None:
            if blocks.first().metadata is None:
                raise InappropriateExit(node.pos, node)
            result.name = blocks.first().metadata
        return result

class SRExit:
    @staticmethod
    def transform(node, st: SymbolTable):
        block_type = None
        match type(node):
            case t if t is basic_ast.ExitWhile:
                block_type = STBlockType.WhileLoopBlock
            case t if t is basic_ast.ExitFunction:
                block_type = STBlockType.FunctionBlock
            case t if t is basic_ast.ExitSubroutine:
                block_type = STBlockType.SubroutineBlock
        if block_type is None:
            raise TypeError(f"Unexpected type {type(node)}")
        if st.bl(block_type).empty():
            raise InappropriateExit(node.pos, node)
        return node

class SRAssignStatement:
    @staticmethod
    def transform(node: basic_ast.AssignStatement, st: SymbolTable):
        result = node
        try:
            result.variable = SemanticRelaxTransform.transform(result.variable, st)
        except UndefinedSymbol as e:
            # Then it's a variable declaration
            if isinstance(result.variable, (basic_ast.ArrayIndex, basic_ast.FuncCall)):
                raise e
            var_decl = basic_ast.VariableDecl(result.pos, result.variable, result.expr)
            return SemanticRelaxTransform.transform(var_decl, st)
        result.expr = SemanticRelaxTransform.transform(result.expr, st)
        if common_type(result.expr.type, result.variable.type) != result.variable.type:
            raise ConversionError(result.pos, result.expr.type, result.variable.type)
        result.expr = ImplicitCastAstGenerator.generate(result.expr, result.variable.type)
        return result

class SRForLoop:
    @staticmethod
    def transform(node: basic_ast.ForLoop, st: SymbolTable):
        result = node
        if not isinstance(node.variable.type, IntegralT):
            raise NotIntFor(node.cond_coord, node.variable.type)
        if SymbolFactory.create(node.variable) != SymbolFactory.create(node.next):
            raise UnexpectedNextFor(node.next_coord, node.variable.name, node.next.name)
        result.start = SemanticRelaxTransform.transform(result.start, st)
        result.end = SemanticRelaxTransform.transform(result.end, st)
        if common_type(result.variable.type, result.start.type) != result.variable.type:
            raise ConversionError(result.start_coord, result.start.type, result.variable.type)
        if common_type(result.variable.type, result.end.type) != result.variable.type:
            raise ConversionError(result.end_coord, result.end.type, result.variable.type)
        result.start = ImplicitCastAstGenerator.generate(result.start, result.variable.type)
        result.end = ImplicitCastAstGenerator.generate(result.end, result.variable.type)
        for_block = st.new_table(STBlockType.ForLoopBlock)
        for_block.add(SymbolFactory.create(result.variable), _is_meta=True)
        for_block.add(SymbolFactory.create(basic_ast.ExitFor(result.variable.pos, result.variable)))
        for idx, statement in enumerate(result.body):
            result.body[idx] = SemanticRelaxTransform.transform(statement, for_block)
        return result

class SRWhileLoop:
    @staticmethod
    def transform(node: basic_ast.WhileLoop, st: SymbolTable):
        result = node
        if result.condition is not None:
            result.condition = SemanticRelaxTransform.transform(result.condition, st)
            if not isinstance(result.condition.type, IntegralT):
                raise WhileNotIntCondition(result.pos, result.condition.type)
        while_block = st.new_table(STBlockType.WhileLoopBlock)
        for idx, statement in enumerate(result.body):
            result.body[idx] = SemanticRelaxTransform.transform(statement, while_block)
        return result

class SRIfStatement:
    @staticmethod
    def transform(node: basic_ast.IfElseStatement, st: SymbolTable):
        result = node
        result.condition = SemanticRelaxTransform.transform(result.condition, st)
        if not isinstance(result.condition.type, IntegralT):
            raise IfNotIntCondition(result.pos, result.condition.type)
        if_block = st.new_table(STBlockType.IfThenBlock)
        for idx, statement in enumerate(result.then_branch):
            result.then_branch[idx] = SemanticRelaxTransform.transform(statement, if_block)
        else_block = st.new_table(STBlockType.IfElseBlock)
        for idx, statement in enumerate(result.else_branch):
            result.else_branch[idx] = SemanticRelaxTransform.transform(statement, else_block)
        return result

class SRImplicitTypeCast:
    @staticmethod
    def transform(node: basic_ast.ImplicitTypeCast, st: SymbolTable):
        return node

class SRUnaryOpExpr:
    @staticmethod
    def transform(node: basic_ast.UnaryOpExpr, st: SymbolTable):
        result = node
        result.unary_expr = SemanticRelaxTransform.transform(result.unary_expr, st)
        if isinstance(result.unary_expr.type, ArrayT) or (not isinstance(result.unary_expr.type, NumericT)):
            raise UnaryBadType(result.pos, result.unary_expr.type, result.op)
        result.type = result.unary_expr.type
        return result

class SRBinaryOpExpr:
    ARITHMETIC_OPERATORS = ('+','-','*','/')
    COMPARISON_OPERATORS = ('<','>','<=','>=','=','<>')

    @staticmethod
    def transform(node: basic_ast.BinOpExpr, st: SymbolTable):
        result = node
        result.left = SemanticRelaxTransform.transform(result.left, st)
        result.right = SemanticRelaxTransform.transform(result.right, st)
        if isinstance(result.left.type, NumericT) or isinstance(result.right.type, NumericT):
            result.type = None
            if result.op in SRBinaryOpExpr.ARITHMETIC_OPERATORS:
                result.type = DoubleT() if result.op == '/' else common_type(result.left.type, result.right.type)
                result.left = ImplicitCastAstGenerator.generate(result.left, result.type)
                result.right = ImplicitCastAstGenerator.generate(result.right, result.type)
            elif result.op in SRBinaryOpExpr.COMPARISON_OPERATORS:
                result.type = BoolT()
            else:
                raise UndefinedBinOperType(result.pos, result.left.type, result.op, result.right.type)
            if result.type is None:
                raise BinBadType(result.pos, result.left.type, result.op, result.right.type)
        elif isinstance(result.left.type, PointerT) and isinstance(result.right.type, PointerT):
            if result.op != '+' or not (isinstance(result.left.type.type, StringT) and isinstance(result.right.type.type, StringT)):
                raise UndefinedBinOperType(result.pos, result.left.type, result.op, result.right.type)
            result.type = PointerT(StringT())
        else:
            raise BinBadType(result.pos, result.left.type, result.op, result.right.type)
        return result

class SRConstExpr:
    @staticmethod
    def transform(node: basic_ast.ConstExpr, st: SymbolTable):
        if isinstance(node.type, StringT):
            #TODO: if it'll stay, need to think about string literal names
            # return basic_ast.VariableReference(node.pos, basic_ast.Varname(node.pos, "str_1", node.type), PointerT(node.type))
            return basic_ast.ImplicitTypeCast(node.pos, PointerT(node.type), node)
        return node