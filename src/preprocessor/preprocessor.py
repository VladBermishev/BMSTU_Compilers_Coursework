import pathlib
from src.preprocessor.analyzers.contains_directives import ContainsDirectives
from src.preprocessor.file_table import FileTable
from src.preprocessor.transforms.include_transform import IncludeTransform
from src.preprocessor.transforms.semantic_relax_transform import SemanticRelaxTransform
from src.preprocessor.grammar import NProgram
import src.libs.parser_edsl as pe

class Preprocessor:
    INCURSION_DEPTH = 100

    def __init__(self):
        self.pp_parser = pe.Parser(NProgram)
        self.pp_parser.add_skipped_domain('[\r\f]+')

    def process(self, source_path: pathlib.Path) -> str:
        current_ast = None
        current_file = source_path
        file_table = FileTable(current_directory=source_path.parent)
        with open(current_file) as f:
            current_ast = self.pp_parser.parse(f.read())
        if ContainsDirectives(current_ast):
            for idx in range(Preprocessor.INCURSION_DEPTH):
                pipeline = [SemanticRelaxTransform(current_file, file_table), IncludeTransform(self.pp_parser, file_table)]
                transformed_ast = pipeline[0].transform(current_ast)
                transformed_ast = pipeline[1].transform(transformed_ast)
                if not ContainsDirectives(transformed_ast):
                    current_ast = transformed_ast
                    break
                file_table = pipeline[1].file_table
                current_ast = transformed_ast
        return '\n'.join(current_ast.source_lines)


if __name__ == '__main__':
    import sys
    file_path = pathlib.Path(sys.argv[-1])
    try:
        pp = Preprocessor()
        with open(file_path.parent/pathlib.Path("preprocessed.basic"), "w") as f:
            f.write(pp.process(file_path))
    except pe.Error as e:
        print(f'{file_path}: Error {e.pos}: {e.message}')


