from src.parser.analyzers.symbol_table import *
from src.parser.basic_ast import *


class SymbolFactory:
    @staticmethod
    def create(node, metadata=None):
        match type(node):
            case t if t is FunctionDef:
                return SymbolFactory.create(node.proto, metadata=metadata)
            case t if t is SubroutineDef:
                return SymbolFactory.create(node.proto, metadata=metadata)
            case t if t is FunctionProto:
                return Symbol(node.name.name, node.type, node.pos, metadata=metadata)
            case t if t is SubroutineProto:
                return Symbol(node.name.name, node.type, node.pos, metadata=metadata)
            case t if t is FunctionDecl or t is SubroutineDecl:
                result = SymbolFactory.create(node.proto, metadata=metadata)
                result.declaration = True
                return result
            case t if t is FuncCallOrArrayIndex:
                return Symbol(node.name.name, node.name.type, node.pos, metadata=metadata)
            case t if t is PrintCall:
                def __print_name(tp: Type):
                    match type(tp):
                        case t if t is PointerT and type(tp.type) is StringT:
                            return f"PrintS"
                    return f"Print{tp.mangle_suff}"
                return [Symbol(__print_name(arg.type), ProcedureT(VoidT(), arg.type), node.pos, metadata=metadata) for arg in node.args]
            case t if t is FuncCall:
                return Symbol(node.name.name, ProcedureT(node.name.type, [arg.type for arg in node.args]), node.pos, metadata=metadata)
            case t if t is ArrayIndex:
                return Symbol(node.name.name, node.name.type, node.pos, metadata=metadata)
            case t if t is ExitFor:
                return Symbol(f"label{node.name.name}", VoidT(), node.pos, metadata=metadata)
            case t if t is Variable:
                return Symbol(node.name.name, node.type, node.pos, metadata=metadata)
            case t if t is Array:
                return Symbol(node.name.name, node.type, node.pos, metadata=metadata)
            case t if t is ArrayReference:
                return Symbol(node.name.name, node.type, node.pos, metadata=metadata)
        return None

    @staticmethod
    def string_length():
        return Symbol("StringLength", ProcedureT(IntegerT(), [PointerT(StringT())]))

    @staticmethod
    def string_copy():
        return Symbol("StringCopy", ProcedureT(PointerT(StringT()), [PointerT(StringT())]))

    @staticmethod
    def string_concat():
        return Symbol("StringCopy", ProcedureT(PointerT(StringT()), [PointerT(StringT()), PointerT(StringT())]))