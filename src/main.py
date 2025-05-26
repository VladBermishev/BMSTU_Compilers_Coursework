import sys
import logging
import argparse
from pathlib import Path

from src.codegen.transform.hir_transform import HirTransform
from src.formatter.ast_formatter import AstTreeFormatter
from src.parser.transforms.semantic_relax_transform import SemanticRelaxTransform
from src.preprocessor.preprocessor import Preprocessor
from src.std_library.std_library import StandardLibrary
from src.parser import basic_grammar
from src.libs import parser_edsl as pe
from src.optimizer.transforms.constant_folding import ConstantFoldingTransform

logger = logging.getLogger(__name__)
compiler_version = "1.0.0"

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser("TBasic compiler driver", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    arg_parser.add_argument("--ast-dump", action="store_true", help="print raw ast tree", required=False, default=False)
    arg_parser.add_argument("--constant-folding", action="store_true", help="[ConstFolding] Transform", required=False, default=False)
    arg_parser.add_argument("--emit-llvm", action="store_true", help="produce llvm-ir", required=False, default=False)
    arg_parser.add_argument("--version", action="store_true", help="print version", required=False, default=False)
    arg_parser.add_argument("source_file", nargs='?', help="source_file", default=None)
    args = arg_parser.parse_args(sys.argv[1:])
    if args.version:
        print(f"tbasic version {compiler_version}")
        sys.exit(0)
    if args.source_file is None or not (Path(args.source_file).exists() and Path(args.source_file).is_file()):
        print(f"fatal error: no input files, can't process given path as source: \"{args.source_file}\"", file=sys.stderr)
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
        logger.info(f"Parsing source file: {args.source_file}")
        preprocessed_source = Preprocessor().process(Path(args.source_file))
        source_ast = basic_parser.parse(preprocessed_source)
        source_ast, source_st = SemanticRelaxTransform.transform(source_ast, standart_library=std_lib_ast)
        if args.constant_folding:
            source_ast = ConstantFoldingTransform.transform(source_ast)
        if args.ast_dump:
            AstTreeFormatter.print(source_ast)
        module = HirTransform.transform(source_ast, source_id=args.source_file)
    except pe.Error as e:
        logger.error(f'{args.source_file}: Error: {e.pos}: {e.message}')