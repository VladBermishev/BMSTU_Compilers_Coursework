from src.parser import basic_ast
from src.parser import basic_types
from src.parser.analyzers.is_const_expr import is_const_expr
from src.parser.basic_types import PointerT


class Transform:
    @staticmethod
    def transform(node):
        raise NotImplementedError()

class ConstantFoldingTransform(Transform):
    @staticmethod
    def transform(node):
        result = node
        match type(node):
            case t if t is basic_ast.Program:
                for idx, decl in enumerate(result.decls):
                    result.decls[idx] = ConstantFoldingTransform.transform(decl)
            case t if t is basic_ast.SubroutineDef:
                for idx, stmt in enumerate(result.body):
                    result.body[idx] = ConstantFoldingTransform.transform(stmt)
            case t if t is basic_ast.FunctionDef:
                for idx, stmt in enumerate(result.body):
                    result.body[idx] = ConstantFoldingTransform.transform(stmt)
            case t if t is basic_ast.VariableDecl:
                result.variable = ConstantFoldingTransform.transform(result.variable)
                result.init_value = ConstantFoldingTransform.transform(result.init_value)
            case t if t is basic_ast.Array:
                for idx, sz in enumerate(result.size):
                    result.size[idx] = ConstantFoldingTransform.transform(sz)
            case t if isinstance(result, basic_ast.Expr):
                result = CFExpr.transform(result)
            case t if t is basic_ast.InitializerList:
                for idx, init_list_val in enumerate(result.values):
                    result.values[idx] = ConstantFoldingTransform.transform(init_list_val)
            case t if t in (basic_ast.FuncCallOrArrayIndex, basic_ast.FuncCall, basic_ast.ArrayIndex, basic_ast.PrintCall):
                for idx, arg in enumerate(result.args):
                    result.args[idx] = ConstantFoldingTransform.transform(arg)
            case t if t is basic_ast.LenCall:
                result.array = ConstantFoldingTransform.transform(result.array)
            case t if t is basic_ast.AssignStatement:
                if isinstance(result.variable, basic_ast.FuncCallOrArrayIndex):
                    result.variable = ConstantFoldingTransform.transform(result.variable)
                result.expr = CFExpr.transform(result.expr)
            case t if t is basic_ast.ForLoop:
                result.start = CFExpr.transform(result.start)
                result.end = CFExpr.transform(result.end)
                for idx, stmt in enumerate(result.body):
                    result.body[idx] = ConstantFoldingTransform.transform(stmt)
            case t if t is basic_ast.WhileLoop:
                if result.condition is not None:
                    result.condition = CFExpr.transform(result.condition)
                for idx, stmt in enumerate(result.body):
                    result.body[idx] = ConstantFoldingTransform.transform(stmt)
            case t if t is basic_ast.IfElseStatement:
                result.condition = CFExpr.transform(result.condition)
            case t if isinstance(node, basic_ast.Expr):
                result.condition = CFExpr.transform(result.condition)
        return result

class CFExpr:
    @staticmethod
    def transform(node):
        result = node
        match type(node):
            case t if t is basic_ast.ConstExpr:
                return result
            case t if t is basic_ast.UnaryOpExpr:
                result = CFUnaryExpr.transform(result)
            case t if t is basic_ast.BinOpExpr:
                result = CFBinaryExpr.transform(result)
            case t if t is basic_ast.ImplicitTypeCast:
                if not type(result.type) is PointerT and is_const_expr(result.expr):
                    result = ConstantFoldingTransform.transform(result.expr)
                    result.type = node.type
        return result


class CFUnaryExpr:
    @staticmethod
    def transform(node):
        result = node
        result.unary_expr = CFExpr.transform(result.unary_expr)
        if isinstance(result.unary_expr, basic_ast.ConstExpr):
            if result.unary_expr.type != basic_types.StringT():
                if isinstance(result.unary_expr.type, basic_types.IntegralT):
                    result = basic_ast.ConstExpr(result.pos, int(f"{result.op}{result.unary_expr.value}"),
                                               result.unary_expr.type)
                elif isinstance(result.unary_expr.type, basic_types.FloatingPointT):
                    result = basic_ast.ConstExpr(result.pos, float(f"{result.op}{result.unary_expr.value}"),
                                               result.unary_expr.type)
        return result


class CFBinaryExpr:
    @staticmethod
    def transform(node):
        result = node
        result.left = CFExpr.transform(result.left)
        result.right = CFExpr.transform(result.right)
        if is_const_expr(result.left) and is_const_expr(result.right):
            if result.left.type == basic_types.StringT() and result.right.type == basic_types.StringT() and result.op == '+':
                result = basic_ast.ConstExpr(result.pos, f"{result.left.value}{result.right.value}", basic_types.StringT())
            elif (result.left.type == basic_types.PointerT(basic_types.StringT()) and
                  result.right.type == basic_types.PointerT(basic_types.StringT())):
                if result.left.type.type == basic_types.StringT() and result.right.type.type == basic_types.StringT() and result.op == '+':
                    concated_length = result.left.type.type.size[0] + result.right.type.type.size[0]
                    concated_string = basic_ast.ConstExpr(result.pos, f"{result.left.expr.value}{result.right.expr.value}", basic_types.StringT(concated_length))
                    result = basic_ast.ImplicitTypeCast(result.pos, basic_types.PointerT(concated_string.type), concated_string)
            elif isinstance(result.left.type, basic_types.NumericT) and isinstance(result.right.type, basic_types.NumericT):
                match result.op:
                    case op if op in ('>', '<', '>=', '<=', '=', '<>'):
                        result.op = "!=" if result.op == "<>" else result.op
                        result.op = "==" if result.op == "=" else result.op
                        result = basic_ast.ConstExpr(result.pos,
                                                     int(eval(f"{result.left.value}{result.op}{result.right.value}")),
                                                     basic_types.BoolT())
                    case op if op in ('+', '-', '*', '/'):
                        if not(op == '/' and result.right.value == 0):
                            result = basic_ast.ConstExpr(result.pos,
                                                         eval(f"{result.left.value}{result.op}{result.right.value}"),
                                                         result.left.type if result.left.type.priority > result.right.type.priority else result.right.type)
        return result
