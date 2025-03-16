import sys
from src.parser import basic_grammar, parser_edsl as pe
from src.optimizer.transforms import ConstantFoldingTransform
import argparse
from pathlib import Path
from pprint import pprint

p = pe.Parser(basic_grammar.NProgram)
p.add_skipped_domain('\\s')
p.add_skipped_domain('\\\'.*?\\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser("TBasic compiler driver", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--ast-dump", action="store_true", help="print raw ast tree", required=False, default=False)
    parser.add_argument("--constant-folding", action="store_true", help="[ConstFolding] Transform", required=False, default=False)
    parser.add_argument("--emit-llvm", action="store_true", help="mqtt broker ip address", required=False, default=False)
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