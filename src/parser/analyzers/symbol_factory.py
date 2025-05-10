from src.parser.analyzers.symbol_table import *
from src.parser.basic_ast import *


class SymbolFactory:
    @staticmethod
    def create(node):
        match type(node):
            case t if t is FunctionDef:
                return SymbolFactory.create(node.proto)
            case t if t is FunctionProto:
                return Symbol(node.name, node.type, node.pos)
            case t if t is FunctionDecl:
                result = SymbolFactory.create(node.proto)
                result.external = True
                return result
            case t if t is FuncCall:
                return Symbol(node.name, ProcedureT(node.name.type, [arg.type for arg in node.args]), node.pos)
            case t if t is ArrayIndex:
                return Symbol(node.name, node.name.type, node.pos)
            case t if t is Variable:
                return Symbol(node.name, node.type, node.pos)
        return None