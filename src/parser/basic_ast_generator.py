from src.parser.basic_ast import *
from src.parser.basic_ast import InitializerList
from src.parser.basic_types import *

class ImplicitCastAstGenerator:

    @staticmethod
    def generate(node, implicit_type: Type) -> Expr | None:
        match type(node):
            case t if t is InitializerList:
                return InitializerListICAGenerator.generate(node, implicit_type)
            case t if t is ConstExpr:
                return ConstExprICAGenerator.generate(node, implicit_type)
            case t if t is FuncCall:
                return FuncCallICAGenerator.generate(node, implicit_type)
            case t if t is VariableDecl:
                return VariableDeclICAGenerator.generate(node, implicit_type)
            case t if t is VariableReference:
                return node
            case t if t is ImplicitTypeCast:
                return ImplicitTypeCast(node.pos, implicit_type, node.expr)
            case t if isinstance(node, Expr) or t is Variable:
                if implicit_type != node.type:
                    return ImplicitTypeCast(node.pos, implicit_type, node)
                return node
        return None

class InitializerListICAGenerator:

    @staticmethod
    def generate(node: InitializerList, implicit_type: Type) -> InitializerList | None:
        result = node
        for idx, value in enumerate(result.values):
            result.values[idx] = ImplicitCastAstGenerator.generate(value, implicit_type)
            if result.values[idx] is None:
                return None
        return result

class ConstExprICAGenerator:
    @staticmethod
    def generate(node: ConstExpr, implicit_type: Type) -> Expr | None:
        if node.type != implicit_type:
            value_type = int if isinstance(implicit_type, IntegralT) else float
            return ConstExpr(node.pos, value_type(node.value), implicit_type)
        return node

class FuncCallICAGenerator:

    @staticmethod
    def generate(node: FuncCall, implicit_type: Type) -> Expr | None:
        result = node
        for idx, arg in enumerate(result.args):
            result.args[idx] = ImplicitCastAstGenerator.generate(arg, implicit_type)
            if result.args[idx] is None:
                return None
        return result

class VariableDeclICAGenerator:
    @staticmethod
    def generate(node: VariableDecl, implicit_type: Type):
        result = node
        if implicit_type != result.init_value.type:
            result.init_value = ImplicitTypeCast(result.init_value.pos, implicit_type, result.init_value)
        return result

