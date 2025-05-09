import sys
import argparse
from pathlib import Path
from pprint import pprint
from src.parser import basic_grammar
from src.libs import parser_edsl as pe
from src.optimizer.transforms.constant_folding import ConstantFoldingTransform


p = pe.Parser(basic_grammar.NProgram)
p.add_skipped_domain('\\s')
p.add_skipped_domain('\\\'.*?\\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser("TBasic compiler driver",
                                     description="TBasic compiler driver",
                                     usage="TBasic compiler driver [options]* <source_file>",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--ast-dump", action="store_true", help="print raw ast tree", required=False, default=False)
    parser.add_argument("--constant-folding", action="store_true", help="[ConstFolding] Transform", required=False, default=False)
    parser.add_argument("--emit-llvm", action="store_true", help="produce llvm-ir", required=False, default=False)
    if len(sys.argv) == 1:
        print("fatal error: no input files", file=sys.stderr, flush=True)
        parser.print_help()
        exit(1)
    args = parser.parse_args(sys.argv[1:-1])
    file_path = sys.argv[-1]
    try:
        with open(file_path) as f:
            tree = p.parse(f.read())
            tree = ConstantFoldingTransform.transform(tree)
            pprint(tree)
            module = tree.codegen()
            # tree.symbol_table.print()
            with open(Path(file_path).with_suffix('').with_suffix('.ll'), "w+") as fout:
                fout.write(str(module))
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')