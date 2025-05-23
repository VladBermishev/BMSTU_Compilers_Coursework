import src.parser.basic_ast as basic_ast


class BasicAstSearch:
    @staticmethod
    def dfs(ast_node, cond):
        if cond(ast_node):
            yield ast_node
        match type(ast_node):
            case t if t is basic_ast.Program:
                for decl in ast_node.decls:
                    if (result := BasicAstSearch.dfs(decl, cond)) is not None:
                        yield result
            case t if t is basic_ast.FunctionDecl or t is basic_ast.SubroutineDecl:
                yield BasicAstSearch.dfs(ast_node.proto, cond)
            case t if t is basic_ast.FunctionDef or t is basic_ast.SubroutineDef:
                if (result := BasicAstSearch.dfs(ast_node.proto, cond)) is not None:
                    yield result
                for statement in ast_node.body:
                    if (result := BasicAstSearch.dfs(statement, cond)) is not None:
                        yield result
            case t if t is basic_ast.VariableDecl:
                if ast_node.init_value is not None:
                    yield BasicAstSearch.dfs(ast_node.init_value, cond)
            case t if t is basic_ast.InitializerList:
                for value in ast_node.values:
                    if (result := BasicAstSearch.dfs(value, cond)) is not None:
                        yield result
            case t if t in (basic_ast.FuncCallOrArrayIndex, basic_ast.PrintCall, basic_ast.FuncCall, basic_ast.ArrayIndex):
                for arg in ast_node.args:
                    if (result := BasicAstSearch.dfs(arg, cond)) is not None:
                        yield result
            case t if t is basic_ast.ExitFor:
                yield BasicAstSearch.dfs(ast_node.name, cond)
            case t if t is basic_ast.AssignStatement:
                if (result := BasicAstSearch.dfs(ast_node.variable, cond)) is not None:
                    yield result
                yield BasicAstSearch.dfs(ast_node.expr, cond)
            case t if t is basic_ast.ForLoop:
                if (result := BasicAstSearch.dfs(ast_node.variable, cond)) is not None:
                    yield result
                if (result := BasicAstSearch.dfs(ast_node.start, cond)) is not None:
                    yield result
                if (result := BasicAstSearch.dfs(ast_node.end, cond)) is not None:
                    yield result
                for statement in ast_node.body:
                    if (result := BasicAstSearch.dfs(statement, cond)) is not None:
                        yield result
                if (result := BasicAstSearch.dfs(ast_node.next, cond)) is not None:
                    yield result
            case t if t is basic_ast.WhileLoop:
                if (result := BasicAstSearch.dfs(ast_node.condition, cond)) is not None:
                    yield result
                for statement in ast_node.body:
                    if (result := BasicAstSearch.dfs(statement, cond)) is not None:
                        yield result
            case t if t is basic_ast.IfElseStatement:
                if (result := BasicAstSearch.dfs(ast_node.condition, cond)) is not None:
                    yield result
                for statement in ast_node.then_branch:
                    if (result := BasicAstSearch.dfs(statement, cond)) is not None:
                        yield result
                if ast_node.else_branch:
                    for statement in ast_node.else_branch:
                        if (result := BasicAstSearch.dfs(statement, cond)) is not None:
                            yield result
            case t if t is basic_ast.ImplicitTypeCast:
                yield BasicAstSearch.dfs(ast_node.expr, cond)
            case t if t is basic_ast.UnaryOpExpr:
                yield BasicAstSearch.dfs(ast_node.unary_expr, cond)
            case t if t is basic_ast.BinOpExpr:
                if (result := BasicAstSearch.dfs(ast_node.left, cond)) is not None:
                    yield result
                yield BasicAstSearch.dfs(ast_node.right, cond)
        return None

    @staticmethod
    def find(ast_node, cond):
        return next(BasicAstSearch.dfs(ast_node, cond))

    @staticmethod
    def find_all(ast_node, cond):
        return list(BasicAstSearch.dfs(ast_node, cond))