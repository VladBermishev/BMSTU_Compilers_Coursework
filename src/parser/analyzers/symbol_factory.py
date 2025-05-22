from src.parser.analyzers.symbol_table import *
from src.parser.basic_ast import *


class SymbolFactory:
    @staticmethod
    def create(node):
        match type(node):
            case t if t is FunctionDef:
                return SymbolFactory.create(node.proto)
            case t if t is SubroutineDef:
                return SymbolFactory.create(node.proto)
            case t if t is FunctionProto:
                return Symbol(node.name.name, node.type, node.pos)
            case t if t is SubroutineProto:
                return Symbol(node.name.name, node.type, node.pos)
            case t if t is FunctionDecl:
                result = SymbolFactory.create(node.proto)
                result.declaration = True
                return result
            case t if t is SubroutineDecl:
                result = SymbolFactory.create(node.proto)
                result.declaration = True
                return result
            case t if t is FuncCallOrArrayIndex:
                return Symbol(node.name.name, node.name.type, node.pos)
            case t if t is FuncCall:
                return Symbol(node.name.name, ProcedureT(node.name.type, [arg.type for arg in node.args]), node.pos)
            case t if t is ArrayIndex:
                return Symbol(node.name.name, node.name.type, node.pos)
            case t if t is ExitFor:
                return Symbol(f"label{node.name.name}", VoidT(), node.pos)
            case t if t is Variable:
                return Symbol(node.name.name, node.type, node.pos)
            case t if t is Array:
                return Symbol(node.name.name, node.type, node.pos)
            case t if t is ArrayReference:
                return Symbol(node.name.name, node.type, node.pos)
        return None