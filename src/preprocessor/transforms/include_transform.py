import src.preprocessor.directives as pp_ast
from src.preprocessor.transforms.semantic_relax_transform import SemanticRelaxTransform
from src.preprocessor.errors import PragmaUnknownCommand, IncludeInvalidPath
from src.preprocessor.file_table import FileTable
import src.libs.parser_edsl as pe


class IncludeTransform:
    def __init__(self, parser:pe.Parser, file_table: FileTable):
        self.parser = parser
        self.file_table = file_table

    def transform(self, node: pp_ast.Program):
        if not isinstance(node, pp_ast.Program):
            raise RuntimeError(f"Node must be {pp_ast.Program}")
        result = pp_ast.Program([])
        for src_line in node.source_lines:
            if isinstance(src_line, pp_ast.FileInclude):
                if (path := self.file_table.find(src_line.filepath)) is not None:
                    with open(path, "r", encoding="utf-8") as fin:
                        try:
                            included_program = self.parser.parse(fin.read())
                            srt = SemanticRelaxTransform(path, self.file_table)
                            srt.transform(included_program)
                            result.source_lines += included_program.source_lines
                            self.file_table = srt.file_table
                        except pe.Error as e:
                            raise RuntimeError(f'{path}: Error {e.pos}: {e.message}')
                else:
                    raise IncludeInvalidPath(src_line.pos, src_line.filepath, self.file_table.locations())
            else:
                result.source_lines.append(src_line)
        return result