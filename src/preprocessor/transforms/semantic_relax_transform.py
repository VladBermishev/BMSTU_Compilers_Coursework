import src.preprocessor.directives as pp_ast
from src.preprocessor.file_table import FileTable
class SemanticRelaxTransform:
    @staticmethod
    def transform(node, ft: FileTable = None):
        result = node
        match type(node):
            case t if t is pp_ast.Program:
                result = pp_ast.Program([])
                for src_line in node.source_lines:
                    if (new_line := SemanticRelaxTransform.transform(src_line, ft)) is not None:
                        result.source_lines.append(new_line)
            case t if t is pp_ast.FileInclude:
                pass
            case t if t is pp_ast.PragmaCommand:
                pass
        return result