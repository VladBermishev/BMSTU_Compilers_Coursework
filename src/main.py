import sys
import logging
import argparse
from pathlib import Path
from pprint import pprint
from src.parser.transforms.semantic_relax_transform import SemanticRelaxTransform
from src.preprocessor.preprocessor import Preprocessor
from src.std_library import StandardLibrary
from src.parser import basic_grammar
from src.libs import parser_edsl as pe
from src.optimizer.transforms.constant_folding import ConstantFoldingTransform

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser("TBasic compiler driver",
                                         usage="TBasic compiler driver [options]* <source_file>",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument("--ast-dump", action="store_true", help="print raw ast tree", required=False, default=False)
    arg_parser.add_argument("--constant-folding", action="store_true", help="[ConstFolding] Transform", required=False, default=False)
    arg_parser.add_argument("--emit-llvm", action="store_true", help="produce llvm-ir", required=False, default=False)
    if len(sys.argv) == 1:
        print("fatal error: no input files", file=sys.stderr)
        sys.exit(1)
    args = arg_parser.parse_args(sys.argv[1:-1])
    file_path = sys.argv[-1]
    if not (Path(file_path).exists() and Path(file_path).is_file()):
        print(f"fatal error: no input files, can't process given path as source: \"{file_path}\"", file=sys.stderr)
        sys.exit(1)
    try:
        basic_parser = pe.Parser(basic_grammar.NProgram)
        basic_parser.add_skipped_domain('\\s')
        basic_parser.add_skipped_domain('\\\'.*?\\n')
        std_lib_ast = None
        if (std_location := StandardLibrary.location()) is not None:
            logger.info(f"Parsing standart library: {std_location}")
            try:
                preprocessed_source = Preprocessor().process(std_location)
                std_lib_ast = basic_parser.parse(preprocessed_source)
            except pe.Error as e:
                logger.error(f'Internal std error: {e.pos}: {e.message}')
        else:
            raise ValueError("Standard library wasn't found, install at default location")
        logger.info(f"Parsing source file: {file_path}")
        preprocessed_source = Preprocessor().process(Path(file_path))
        source_ast = basic_parser.parse(preprocessed_source)
        source_ast, source_st = SemanticRelaxTransform.transform(source_ast, standart_library=std_lib_ast)
        if args.constant_folding:
            source_ast = ConstantFoldingTransform.transform(source_ast)
        pprint(source_ast)
    except pe.Error as e:
        logger.error(f'{file_path}: Error: {e.pos}: {e.message}')