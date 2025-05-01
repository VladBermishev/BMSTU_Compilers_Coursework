from src.parser import basic_ast

def IsConstExpr(ast_node: basic_ast.Expr):
    if not isinstance(ast_node, basic_ast.Expr):
        raise TypeError("Expected an <Expr>")
    match type(ast_node):
        case t if t is basic_ast.ConstExpr:
            return True
        case t if t is basic_ast.UnaryOpExpr:
            return IsConstExpr(ast_node.unary_expr)
        case t if t is basic_ast.BinOpExpr:
            return IsConstExpr(ast_node.left) and IsConstExpr(ast_node.right)
    return False