from src.parser import basic_ast

def is_const_expr(ast_node: basic_ast.Expr):
    match type(ast_node):
        case t if t is basic_ast.ConstExpr:
            return True
        case t if t is basic_ast.UnaryOpExpr:
            return is_const_expr(ast_node.unary_expr)
        case t if t is basic_ast.BinOpExpr:
            return is_const_expr(ast_node.left) and is_const_expr(ast_node.right)
        case t if t is basic_ast.InitializerList:
            return all([is_const_expr(value) for value in ast_node.values])
        case t if t is basic_ast.ImplicitTypeCast:
            return is_const_expr(ast_node.expr)
    return False