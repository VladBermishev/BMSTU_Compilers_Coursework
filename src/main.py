import os
import subprocess
import sys
import logging
import argparse

from pathlib import Path
from src.codegen.transform.hir_transform import HirTransform
from src.codegen.transform.llvm_ir_transform import LLVMTransform
from src.formatter.ast_formatter import AstTreeFormatter
from src.formatter.hir_formatter import HirTreeFormatter
from src.formatter.llvm_formatter import LLVMFormatter
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
    arg_parser.add_argument("--ast-dump", action="store_true", help="print ast tree", required=False, default=False)
    arg_parser.add_argument("--constant-folding", action="store_true", help="[ConstFolding] Transform", required=False, default=False)
    arg_parser.add_argument("--emit-llvm", action="store_true", help="produce llvm-ir", required=False, default=False)
    arg_parser.add_argument("--emit-hir", action="store_true", help="produce hir", required=False, default=False)
    arg_parser.add_argument("--emit-intel-asm", action="store_true", help="produce asm", required=False, default=False)
    arg_parser.add_argument("--version", action="store_true", help="print version", required=False, default=False)
    arg_parser.add_argument("--output", help="outfile", required=False, default=None)
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
        if (std_location := StandardLibrary.location(Path("std.basic"))) is not None:
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
    except pe.Error as e:
        logger.error(f'{args.source_file}: Error: {e.pos}: {e.message}')
        exit(1)

    if args.constant_folding:
        source_ast = ConstantFoldingTransform.transform(source_ast)
    if args.ast_dump:
        AstTreeFormatter.print(source_ast)
        sys.exit(0)
    module = HirTransform.transform(source_ast, source_id=args.source_file)
    if args.emit_hir:
        HirTreeFormatter.print(module)
        sys.exit(0)
    llvm_module = LLVMTransform.transform(module)
    if args.emit_llvm:
        LLVMFormatter.print(llvm_module)
        sys.exit(0)
    outfile_path = Path(args.source_file).parent / "a.out"
    if args.output is not None:
        outfile_path = Path(args.output)
    with open(outfile_path.with_suffix('.ll'), "w") as fout:
        LLVMFormatter.print(llvm_module, file=fout)
    if args.emit_intel_asm:
        subprocess.run(["llc", "-filetype=asm", "--x86-asm-syntax=intel",
                        outfile_path.with_suffix('.ll'), "-o", outfile_path.with_suffix('.s')])
        sys.exit(0)

    subprocess.run(["llc", "-filetype=obj", outfile_path.with_suffix('.ll'), "-o", outfile_path.with_suffix('.o')])
    subprocess.run(["clang", StandardLibrary.location(Path("std.o")), outfile_path.with_suffix('.o'), "-o", outfile_path,"-lstdc++"])