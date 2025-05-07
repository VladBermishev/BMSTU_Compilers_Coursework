import re
from src.libs import parser_edsl as pe
from src.preprocessor.directives import Program, FileInclude, PragmaCommand

def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None, re_flags=re.IGNORECASE, priority=10)

EPS = lambda:[]
FILEPATH = pe.Terminal('FILEPATH', '(?:/[^/]+)*?/?\w+(?:\.\w+)?', str)
TEXT = pe.Terminal('TEXT', '[^\n]+', str)

KW_INCLUDE, KW_PRAGMA = map(make_keyword, '#include #pragma'.split())
NProgram, NLines, NLine, NControlLine = map(pe.NonTerminal, "Program Lines Line ControlLine".split())

NProgram |= NLines, Program.create
NProgram |= EPS
NLines |= NLine, '\n', NLines, lambda l, ls: [l] + ls
NLines |= NLine, lambda l: [l]
NLine |= NControlLine
NLine |= TEXT
NControlLine |= KW_INCLUDE, '\"', FILEPATH, '\"', FileInclude.create
NControlLine |= KW_INCLUDE, '<', FILEPATH, '>', FileInclude.create
NControlLine |= KW_PRAGMA, TEXT, PragmaCommand.create

preprocessor = pe.Parser(NProgram)
preprocessor.add_skipped_domain('[\r\t\f ]+')
preprocessor.add_skipped_domain('\\\'.*?\\n')


