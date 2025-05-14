import abc
from dataclasses import dataclass
from src.parser.errors import *
from src.parser.basic_types import *


class Expr(abc.ABC):
    def __init__(self):
        self.type = Type()

class Statement(abc.ABC):
    pass

@dataclass
class Varname:
    pos: pe.Position
    name: str
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, type = attrs
        cvarname, ctype = coords
        return Varname(cvarname.start, varname, type)

    def __str__(self):
        return f"Varname <line:{self.pos.line}, col:{self.pos.col}> \'{self.name}\' \'{self.type}\'"

@dataclass
class ConstExpr(Expr):
    pos: pe.Position
    value: typing.Any
    type: Type

    @staticmethod
    @pe.ExAction
    def create_int(attrs, coords, res_coord):
        value = attrs[0]
        cvalue = coords[0]
        return ConstExpr(cvalue.start, value, IntegerT())

    @staticmethod
    @pe.ExAction
    def create_float(attrs, coords, res_coord):
        value = attrs[0]
        cvalue = coords[0]
        return ConstExpr(cvalue.start, value, FloatT())

    @staticmethod
    @pe.ExAction
    def create_string(attrs, coords, res_coord):
        value = attrs[0]
        cvalue = coords[0]
        value = value[1:-1].replace("\\n", '\n').replace("\\t", ' ' * 4)
        return ConstExpr(cvalue.start, value, StringT(length=len(value)))

@dataclass
class Variable:
    pos: pe.Position
    name: Varname
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname = attrs[0]
        cvarname = coords[0]
        return Variable(cvarname.start, varname, varname.type)

@dataclass
class VariableReference(Variable):
    pass

@dataclass
class Array(Variable):
    size: list[Expr]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, sizes = attrs
        cvarname, cop, cexpr, ccp = coords
        return Array(cvarname.start, varname, ArrayT(varname.type, sizes), sizes)

@dataclass
class ArrayReference(Array):
    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, dimensions = attrs
        cvarname, cop, cexpr, ccp = coords
        size = [0] * dimensions
        expression_sizes = [ConstExpr(cop.start, 0, IntegerT())] * dimensions
        return ArrayReference(cvarname.start, varname, PointerT(ArrayT(varname.type, size)), expression_sizes)

@dataclass
class FunctionProto:
    pos: pe.Position
    name: Varname
    args: list[Variable]
    type: ProcedureT

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, args = attrs
        cfunc_kw, cvar, cop, cparams, ccp = coords
        return FunctionProto(cvar.start, name, args, ProcedureT(name.type, [arg.type for arg in args]))

@dataclass
class FunctionDecl:
    pos: pe.Position
    proto: FunctionProto
    external: bool

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto = attrs[0]
        cdecl_kw, cproto = coords
        return FunctionDecl(cdecl_kw.start, proto, True)

@dataclass
class FunctionDef:
    pos: pe.Position
    proto: FunctionProto
    body: list[Statement]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto, stmts = attrs
        cfunproto, cbody, cend_kw, cfun_kw = coords
        return FunctionDef(cfunproto.start, proto, stmts)

@dataclass
class SubroutineProto:
    pos: pe.Position
    name: Varname
    args: list[Variable]
    type: ProcedureT

    @pe.ExAction
    def create(attrs, coords, res_coord):
        name, args = attrs
        csub_kw, cvar, cop, cparams, ccp = coords
        varname = Varname(cvar.start, name, VoidT())
        return SubroutineProto(csub_kw.start, varname, args, ProcedureT(VoidT(), [arg.type for arg in args]))

@dataclass
class SubroutineDecl:
    pos: pe.Position
    proto: SubroutineProto
    external: bool

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto = attrs[0]
        cdecl_kw, cproto = coords
        return SubroutineDecl(cdecl_kw.start, proto, True)

@dataclass
class SubroutineDef:
    pos: pe.Position
    proto: SubroutineProto
    body: list[Statement]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        proto, stmts = attrs
        csubproto, cbody, cend_kw, csub_kw = coords
        return SubroutineDef(csubproto.start, proto, stmts)

@dataclass
class InitializerList:
    pos: pe.Position
    values: list[Expr | list]
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        vals = attrs[0]
        cop, cvalues, ccp = coords
        return InitializerList(cop.start, vals, VoidT())

@dataclass
class VariableDecl:
    pos: pe.Position
    variable: Variable
    init_value: typing.Optional[Expr | InitializerList | None]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        var, var_ini = attrs[0], attrs[1] if len(attrs) > 1 else None
        cdim_kw, cvar, cvar_init = coords
        return VariableDecl(cdim_kw.start, var, var_ini)

@dataclass
class FuncCallOrArrayIndex:
    pos: pe.Position
    name: Varname
    args: list[Expr]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, args = attrs
        cvarname, cop, cargs, ccp = coords
        return FuncCallOrArrayIndex(cvarname.start, varname, args)

@dataclass
class PrintCall:
    pos: pe.Position
    args: list[Expr]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        args = attrs[0]
        cprint, cargs = coords
        return PrintCall(cprint.start, args)

@dataclass
class FuncCall(Expr):
    pos: pe.Position
    name: Varname
    args: list[Expr]
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        func_name, args = attrs
        cfunc, cop, cargs, ccp = coords
        if isinstance(func_name, str):
            func_name = Varname(cfunc.start, func_name, VoidT())
        return FuncCall(cfunc.start, func_name, args, func_name.type)

@dataclass
class ArrayIndex(Expr):
    pos: pe.Position
    name: Varname
    args: list[Expr]
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pass


@dataclass
class ExitStatement(Statement):
    pos: pe.Position

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pass


@dataclass
class ExitFor(ExitStatement):
    name: Variable | None

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        var = None
        if len(attrs) != 0:
            varname = attrs[0]
            var = Variable(varname.pos, varname, varname.type)
        cexit = coords[0]
        return ExitFor(cexit.start, var)

@dataclass
class ExitWhile(ExitStatement):

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cexit, cdo = coords
        return ExitWhile(cexit.start)

@dataclass
class ExitSubroutine(ExitStatement):

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cexit, csub = coords
        return ExitSubroutine(cexit.start)

@dataclass
class ExitFunction(ExitStatement):

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cexit, cfunc = coords
        return ExitFunction(cexit.start)

@dataclass
class AssignStatement(Statement):
    pos: pe.Position
    variable: Variable | FuncCallOrArrayIndex
    expr: Expr

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        var, expr = attrs
        if isinstance(var, Varname):
            var = Variable(var.pos, var, var.type)
        cvar, ceq, cexpr = coords
        return AssignStatement(cvar.start, var, expr)

@dataclass
class ForLoop(Statement):
    pos: pe.Position
    variable: Variable
    cond_coord: pe.Position
    start: Expr
    start_coord: pe.Fragment
    end: Expr
    end_coord: pe.Fragment
    body: list[Statement]
    next: Variable
    next_coord: pe.Fragment

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, start, end, body, next_varname = attrs
        cfor_kw, cvar, cass, cstart, cto_kw, cend, cstmts, ckw_next, cnext_varname = coords
        var = Variable(varname.pos, varname, varname.type)
        next_variable = Variable(next_varname.pos, next_varname, next_varname.type)
        return ForLoop(cfor_kw.start, var, cvar.start, start, cstart, end, cend, body, next_variable, cnext_varname)

@dataclass
class WhileLoop(Statement):
    pos: pe.Position
    condition: Expr | None
    body: list[Statement]
    type: WhileType

    @staticmethod
    @pe.ExAction
    def create_pre_while(attrs, coords, res_coord):
        cond, body = attrs[0]
        cwhile_kw, cloop = coords
        return WhileLoop(cwhile_kw.start, cond, body, WhileType.PreWhile)

    @staticmethod
    @pe.ExAction
    def create_pre_until(attrs, coords, res_coord):
        cond, body = attrs[0]
        cwhile_kw, cloop = coords
        return WhileLoop(cwhile_kw.start, cond, body, WhileType.PreUntil)

    @staticmethod
    @pe.ExAction
    def digest(attrs, coords, res_coord):
        body = attrs[0]
        loop_type, cond = attrs[1]
        cdo_kw, ccond, cthen_kw = coords
        return WhileLoop(cdo_kw.start, cond, body, loop_type)

    def __repr__(self):
        return f"While(type={self.type})"


@dataclass
class IfElseStatement(Statement):
    pos: pe.Position
    condition: Expr
    then_branch: list[Statement]
    else_branch: list[Statement]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        cond, then_branch, else_branch = attrs
        cif, ccond, cthen_kw, cthen_br, celse_stmt, cend_kw, cif_kw = coords
        return IfElseStatement(ccond.start, cond, then_branch, else_branch)

@dataclass
class ImplicitTypeCast(Expr):
    pos: pe.Position
    type: Type
    expr: Expr

@dataclass
class UnaryOpExpr(Expr):
    pos: pe.Position
    op: str
    unary_expr: Expr
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        op, left = attrs
        cop, cleft = coords
        return UnaryOpExpr(cop.start, op, left, Type())

@dataclass
class BinOpExpr(Expr):
    pos: pe.Position
    left: Expr
    op: str
    right: Expr
    type: Type

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        left, op, right = attrs
        cleft, cop, cright = coords
        return BinOpExpr(cleft.start, left, op, right, Type())

@dataclass
class Program:
    decls: list[SubroutineDecl | FunctionDecl | SubroutineDef | FunctionDef | VariableDecl]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        global_decls = attrs[0]
        program = Program(global_decls)
        return program