from pathlib import Path
from pprint import pprint

import parser_edsl as pe
import sys
import grammar

p = pe.Parser(grammar_v2.NProgram)
p.add_skipped_domain('\\s')
p.add_skipped_domain('\\\'.*?\\n')

for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            pprint(tree)
            module = tree.codegen()
            #tree.symbol_table.print()
            with open(Path(filename).with_suffix('').with_suffix('.ll'), "w+") as fout:
                fout.write(str(module))
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
