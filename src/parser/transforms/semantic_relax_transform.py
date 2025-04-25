from unittest import case

from src.parser import basic_ast
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
        if sum(1 if isinstance(arg.type, VariadicArgumentT) else 0 for arg in result.args) > 1:
            raise MultipleVariadicArgumentsInProtoError(result.name.pos)
        names = [node.name]
        for idx, var in enumerate(node.args):
            if var.name in names:
                raise RedefinitionError(var.pos, var.name, names[names.index(var.name)].pos)
            if isinstance(var, VariadicArgumentT) and idx != len(node.args) - 1:
                raise VariadicArgumentsInProtoNotLastError(var.pos)
            if isinstance(var.type, ArrayT):
                var.type.is_function_param = True
        return result

class SRInitializerList:
    @staticmethod
    def transform(node: basic_ast.InitializerList, st: SymbolTable = None):
        result = node

        return result