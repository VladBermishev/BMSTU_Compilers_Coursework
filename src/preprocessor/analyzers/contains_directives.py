import src.preprocessor.directives as pp_ast

def ContainsDirectives(ast_node):
    match type(ast_node):
        case t if t is pp_ast.Program:
            result = False
            for line in ast_node.source_lines:
                result |= ContainsDirectives(line)
            return result
        case t if t is pp_ast.FileInclude:
            return True
        case t if t is pp_ast.PragmaCommand:
            return True
    return False