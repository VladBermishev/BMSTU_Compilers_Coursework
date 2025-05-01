from src.parser import basic_ast
from src.parser.basic_ast_generator import ImplicitCastAstGenerator
from src.parser.basic_types import *
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import SymbolTable, Symbol, STLookupStrategy, STLookupScope, STBlockType
from src.parser.errors import *


class SemanticRelaxTransform:

    @staticmethod
    def transform(node, st: SymbolTable = None):
        match type(node):
            case t if t is basic_ast.Program:
                return SRProgram.transform(node)
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
        return None


class SRProgram:
    @staticmethod
    def transform(node: basic_ast.Program):
        table = SymbolTable()
        result = node
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
        result.proto = SemanticRelaxTransform.transform(result.proto, st=st)
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
            result.values[idx] = SemanticRelaxTransform.transform(value, st=st)
        if isinstance(result.values[0], basic_ast.InitializerList):
            if not all(SRInitializerList.dimensions(result.values[0]) == SRInitializerList.dimensions(value) for value in result.values):
                for value in result.values:
                    if SRInitializerList.dimensions(result.values[0]) != SRInitializerList.dimensions(value):
                        raise InappropriateInitializerList(result.pos, SRInitializerList.dimensions(result.values[0]), SRInitializerList.dimensions(value))
        init_type = SRInitializerList.common_type(result)
        if init_type:
            result = ImplicitCastAstGenerator.generate(result, init_type)
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
