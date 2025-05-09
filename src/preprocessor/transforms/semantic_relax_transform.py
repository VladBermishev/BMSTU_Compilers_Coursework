import src.preprocessor.directives as pp_ast
from src.preprocessor.errors import PragmaUnknownCommand, IncludeInvalidPath
from src.preprocessor.file_table import FileTable
from pathlib import Path

class SemanticRelaxTransform:
    def __init__(self, current_file: Path, file_table: FileTable):
        self.current_file = current_file
        self.file_table = file_table

    def transform(self, node):
        result = node
        match type(node):
            case t if t is pp_ast.Program:
                result = pp_ast.Program([])
                for src_line in node.source_lines:
                    if (new_line := self.transform(src_line)) is not None:
                        result.source_lines.append(new_line)
            case t if t is pp_ast.FileInclude:
                if not self.file_table.find(Path(result.filepath)):
                    if not self.file_table.is_excluded(Path(result.filepath)):
                        raise IncludeInvalidPath(node.pos, node.filepath, self.file_table.locations())
                    return None
                result.filepath = Path(result.filepath)
            case t if t is pp_ast.PragmaCommand:
                if node.command == pp_ast.PragmaCommands.ONCE.value:
                    self.file_table.exclude(self.current_file)
                    return None
                else:
                    raise PragmaUnknownCommand(node.pos, node.command)
        return result