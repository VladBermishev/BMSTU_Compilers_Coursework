import re
from src.libs import parser_edsl as pe
from src.parser.basic_ast import *
from src.parser.basic_types import *

def make_keyword(image):
    return pe.Terminal(image, image, lambda name: None, re_flags=re.IGNORECASE, priority=10)

IDENTIFIER = pe.Terminal('IDENTIFIER', '[A-Za-z][A-Za-z0-9_]*', str)
INTEGER = pe.Terminal('INTEGER', '[0-9]+', int)
STRING = pe.Terminal('STRING', '\"[^\"]*\"', str)
FLOAT = pe.Terminal('FLOAT', '[0-9]+\\.([0-9]*)?(e[-+]?[0-9]+)?', float)


KW_SUB, KW_FUNCTION, KW_END, KW_DIM = map(make_keyword, 'sub function end dim'.split())
KW_EXIT, KW_DECLARE, KW_PRINT = map(make_keyword, "exit declare print".split())
KW_IF, KW_THEN, KW_ELSE, KW_UNTIL, KW_WHILE, KW_DO, KW_FOR, KW_TO, KW_NEXT, KW_LOOP = \
    map(make_keyword, 'if then else until while do for to next loop'.split())

NProgram, NGlobalSymbols, NGlobalSymbol, NSubroutineProto, NFunctionProto, NSubroutineDef, NFunctionDef = \
    map(pe.NonTerminal, "Program GlobalSymbols GlobalSymbol SubroutineProto FunctionProto SubroutineDef FunctionDef".split())

NSubroutineDecl, NFunctionDecl, NVariableDecl, NVariableInit, NInitializerList, NInitializerListValues = \
    map(pe.NonTerminal, "SubroutineDecl FunctionDecl VariableDecl VariableInit InitializerList InitializerListValues".split())

NInitializerListValue, NParametersList, NVarnameOrArrayParam, NCommaList, NVarnameOrArrayArg = \
    map(pe.NonTerminal, "InitializerListValue ParametersList VarnameOrArrayParam CommaList VarnameOrArrayArg".split())

NArgumentsList, NFuncCallOrArrayIndex, NFuncCall, NVarname, NType, NStatements, NStatement, NAssignStatement = \
    map(pe.NonTerminal, "ArgumentsList FuncCallOrArrayIndex FuncCall Varname Type Statements Statement AssignStatement".split())

NNonEmptyArgumentsList, NNonEmptyParametersList, NNonEmptyStatements = \
    map(pe.NonTerminal, "NonEmptyArgumentsList NonEmptyParametersList NonEmptyStatements".split())

NExitStatement, NElseStatement, NLoop, NForLoop, NWhileLoop, NPreOrPostLoop = \
    map(pe.NonTerminal, "ExitStatement ElseStatement Loop ForLoop WhileLoop PreOrPostLoop".split())

NPreLoop, NPostLoop, NPostLoopExpr = \
    map(pe.NonTerminal, "PreLoop PostLoop PostLoopExpr ".split())

NExpr, NCmpOp, NArithmExpr, NAddOp, NTerm, NPower, NConst, NMulOp = \
    map(pe.NonTerminal, 'Expr CmpOp ArithmExpr AddOp Term Power Const MulOp'.split())

NProgram |= NGlobalSymbols, Program.create

NGlobalSymbols |= NGlobalSymbol, NGlobalSymbols, lambda vd, vds: [vd] + vds
NGlobalSymbols |= lambda: []
NGlobalSymbol |= NSubroutineDecl
NGlobalSymbol |= NSubroutineDef
NGlobalSymbol |= NFunctionDecl
NGlobalSymbol |= NFunctionDef
NGlobalSymbol |= NVariableDecl

NSubroutineProto |= KW_SUB, IDENTIFIER, "(", NParametersList, ")", SubroutineProto.create
NFunctionProto |= KW_FUNCTION, NVarname, "(", NParametersList, ")", FunctionProto.create
NSubroutineDef |= NSubroutineProto, NStatements, KW_END, KW_SUB, SubroutineDef.create
NFunctionDef |= NFunctionProto, NStatements, KW_END, KW_FUNCTION, FunctionDef.create
NSubroutineDecl |= KW_DECLARE, NSubroutineProto, SubroutineDecl.create
NFunctionDecl |= KW_DECLARE, NFunctionProto, FunctionDecl.create
NVariableDecl |= KW_DIM, NVarnameOrArrayArg, NVariableInit, VariableDecl.create

NVariableInit |= '=', NExpr
NVariableInit |= '=', NInitializerList
NVariableInit |= lambda: None
NInitializerList |= '{', NInitializerListValues, '}', InitializerList.create
NInitializerList |= '{}', InitializerList.create
NInitializerListValues |= NInitializerListValue, ',', NInitializerListValues, lambda v, vs: [v] + vs
NInitializerListValues |= NInitializerListValue, lambda v: [v]
NInitializerListValue |= NExpr
NInitializerListValue |= NInitializerList

NParametersList |= NVarnameOrArrayParam, ",", NNonEmptyParametersList, lambda vd, vds: [vd] + vds
NParametersList |= NVarnameOrArrayParam, lambda vd: [vd]
NParametersList |= lambda: []

NNonEmptyParametersList |= NVarnameOrArrayParam, ",", NNonEmptyParametersList, lambda vd, vds: [vd] + vds
NNonEmptyParametersList |= NVarnameOrArrayParam, lambda vd: [vd]

NCommaList |= ',', NCommaList, lambda vs: 1 + vs
NCommaList |= lambda: 1

NVarnameOrArrayParam |= NVarname, Variable.create
NVarnameOrArrayParam |= NVarname, "(", NCommaList, ")", ArrayReference.create

NArgumentsList |= NExpr, ",", NNonEmptyArgumentsList, lambda vd, vds: [vd] + vds
NArgumentsList |= NExpr, lambda vd: [vd]
NArgumentsList |= lambda: []

NNonEmptyArgumentsList |= NExpr, ",", NNonEmptyArgumentsList, lambda vd, vds: [vd] + vds
NNonEmptyArgumentsList |= NExpr, lambda vd: [vd]

NVarnameOrArrayArg |= NVarname, Variable.create
NVarnameOrArrayArg |= NVarname, "(", NNonEmptyArgumentsList, ")", Array.create
NVarnameOrArrayArg |= NVarname, "(", NCommaList, ")", Array.create #array declaration with initializer-list

NFuncCallOrArrayIndex |= NVarname, "(", NArgumentsList, ")", FuncCallOrArrayIndex.create
NFuncCallOrArrayIndex |= IDENTIFIER, "(", NArgumentsList, ")", FuncCall.create

NFuncCall |= KW_PRINT, NNonEmptyArgumentsList, PrintCall.create

NVarname |= IDENTIFIER, NType, Varname.create
NType |= "%", lambda: IntegerT()
NType |= "&", lambda: LongT()
NType |= "!", lambda: FloatT()
NType |= "#", lambda: DoubleT()
NType |= '$', lambda: PointerT(StringT())
NType |= '@', lambda: Type()

NStatements |= NStatement, NNonEmptyStatements, lambda vd, vds: [vd] + vds
NStatements |= NExitStatement, lambda vd: [vd]
NStatements |= NStatement, lambda vd: [vd]
NStatements |= lambda: []

NNonEmptyStatements |= NStatement, NNonEmptyStatements, lambda vd, vds: [vd] + vds
NNonEmptyStatements |= NExitStatement, lambda vd: [vd]
NNonEmptyStatements |= NStatement, lambda vd: [vd]

NStatement |= NVariableDecl
NStatement |= NAssignStatement
NStatement |= NFuncCallOrArrayIndex, "=", NExpr, AssignStatement.create
NStatement |= NFuncCallOrArrayIndex
NStatement |= NFuncCall
NStatement |= NLoop
NStatement |= KW_IF, NExpr, KW_THEN, NStatements, NElseStatement, KW_END, KW_IF, IfElseStatement.create

NAssignStatement |= NVarname, "=", NExpr, AssignStatement.create

NExitStatement |= KW_EXIT, KW_FOR, ExitFor.create
NExitStatement |= KW_EXIT, KW_FOR, NVarname, ExitFor.create
NExitStatement |= KW_EXIT, KW_DO, ExitWhile.create
NExitStatement |= KW_EXIT, KW_LOOP, ExitWhile.create
NExitStatement |= KW_EXIT, KW_SUB, ExitSubroutine.create
NExitStatement |= KW_EXIT, KW_FUNCTION, ExitFunction.create

NElseStatement |= KW_ELSE, NStatements
NElseStatement |= lambda: []

NLoop |= NForLoop
NLoop |= NWhileLoop

NForLoop |= KW_FOR, NVarname, "=", NExpr, KW_TO, NExpr, NStatements, KW_NEXT, NVarname, ForLoop.create

NWhileLoop |= KW_DO, NPreOrPostLoop

#NPreOrPostLoop |= KW_WHILE, NPreLoop, lambda expr_and_stmts: WhileLoop(expr_and_stmts[1], expr_and_stmts[0], WhileType.PreWhile)
NPreOrPostLoop |= KW_WHILE, NPreLoop, WhileLoop.create_pre_while
#NPreOrPostLoop |= KW_UNTIL, NPreLoop, lambda expr_and_stmts: WhileLoop(expr_and_stmts[1], expr_and_stmts[0], WhileType.PreUntil)
NPreOrPostLoop |= KW_UNTIL, NPreLoop, WhileLoop.create_pre_until
NPreOrPostLoop |= NPostLoop

NPreLoop |= NExpr, NStatements, KW_LOOP, lambda expr, stmts: (expr, stmts)

NPostLoop |= NStatements, KW_LOOP, NPostLoopExpr, WhileLoop.digest

NPostLoopExpr |= KW_WHILE, NExpr, lambda expr: (WhileType.PostWhile, expr)

NPostLoopExpr |= KW_UNTIL, NExpr, lambda expr: (WhileType.PostUntil, expr)

NPostLoopExpr |= lambda: (WhileType.Endless, None)

NExpr |= NArithmExpr
NExpr |= NArithmExpr, NCmpOp, NArithmExpr, BinOpExpr.create


def op_builder(x):
    def op():
        return x
    return op

for op in ('>', '<', '>=', '<=', '=', '<>'):
    NCmpOp |= op, op_builder(op)

NArithmExpr |= NTerm
NArithmExpr |= NAddOp, NTerm, UnaryOpExpr.create
NArithmExpr |= NArithmExpr, NAddOp, NTerm, BinOpExpr.create

NAddOp |= '+', lambda: '+'
NAddOp |= '-', lambda: '-'

NTerm |= NPower
NTerm |= NTerm, NMulOp, NPower, BinOpExpr.create

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'

NPower |= NVarname, Variable.create
NPower |= NConst
NPower |= '(', NExpr, ')'
NPower |= NFuncCallOrArrayIndex

NConst |= INTEGER, ConstExpr.create_int
NConst |= FLOAT, ConstExpr.create_float
NConst |= STRING, ConstExpr.create_string

if __name__ == "__main__":
    p = pe.Parser(NProgram)
    if not p.is_lalr_one():
        p.print_table()
        assert p.is_lalr_one()
