import re
from src.libs import parser_edsl as pe
from src.preprocessor.directives import Program, FileInclude, PragmaCommand

make_kw = lambda image: pe.Terminal(image, image, lambda name: name, re_flags=re.IGNORECASE, priority=10)
TRAP = lambda *args: None
EPS = lambda *args:""

KW_INCLUDE, KW_PRAGMA = map(make_kw, '#include #pragma'.split())
FILEPATH_CHAR = pe.Terminal('FILEPATH_CHAR', r'[^\n\"<>]', str, priority=1)
NProgram, NLines, NLine, NControlLine = map(pe.NonTerminal, "Program Lines Line ControlLine".split())
NText, NFilepath, NChar, NSpaces, NSpace = map(pe.NonTerminal, "Text Filepath Char Spaces Space".split())

NProgram |= NLines, Program.create
NLines |= NLine, '\n', NLines, lambda l, ls: [l] + ls
NLines |= NLine, lambda l: [l]
NLine |= NControlLine
NLine |= NText
NLine |= EPS
NControlLine |= KW_INCLUDE, NSpaces, '\"', NFilepath, '\"', FileInclude.create
NControlLine |= KW_INCLUDE, NSpaces, '<', NFilepath, '>', FileInclude.create
NControlLine |= KW_PRAGMA, NText, PragmaCommand.create

NSpaces |= NSpace, NSpaces, TRAP
NSpaces |= EPS
NSpace |= ' ', lambda: ' '
NSpace |= '\t', lambda: '\t'

NText |= NChar, NText, lambda l="", ls="": l + ls
NText |= NChar, lambda l="": l
NChar |= FILEPATH_CHAR
NChar |= NSpace
NChar |= '\"', lambda: '\"'
NChar |= '<', lambda: '<'
NChar |= '>', lambda: '>'

NFilepath |= FILEPATH_CHAR, NFilepath, lambda l="", ls="": l + ls
NFilepath |= FILEPATH_CHAR, lambda l="": l


if __name__ == '__main__':
    import sys
    pp_parser = pe.Parser(NProgram)
    pp_parser.add_skipped_domain('[\r\f]+')
    if not pp_parser.is_lalr_one():
        pp_parser.print_table()
        assert pp_parser.is_lalr_one()
    file_path = sys.argv[-1]
    try:
        with open(file_path) as f:
            tree = pp_parser.parse(f.read())
            print(tree)
    except pe.Error as e:
        print(f'{file_path}: Error {e.pos}: {e.message}')