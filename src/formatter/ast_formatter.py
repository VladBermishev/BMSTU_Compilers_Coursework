import sys

from src.formatter.tree import TreeFormatterNode, TreeFormatter
import src.parser.basic_ast as basic_ast

class AstTreeFormatter(TreeFormatter):
    @staticmethod
    def print(node, file=sys.stdout):
        TreeFormatter.print(AstFormatterNode.create(node), file=sys.stdout)

class AstFormatterNode(TreeFormatterNode):
    def __init__(self, title=None, node=None):
        if title is not None:
            super().__init__(title)
        elif node is not None:
            super().__init__(f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.name}\' \'{node.type}\'")

    def __len__(self):
        return 0

    def __iter__(self):
        if False:
            yield self

    @staticmethod
    def create(node):
        match type(node):
            case t if t is basic_ast.ConstExpr:
                return ConstExprFormatterNode(node)
            case t if t is basic_ast.Variable:
                return VariableFormatterNode(node)
            case t if t is basic_ast.VariableReference:
                return VariableReferenceFormatterNode(node)
            case t if t is basic_ast.Array:
                return ArrayFormatterNode(node)
            case t if t is basic_ast.ArrayReference:
                return ArrayReferenceFormatterNode(node)
            case t if t is basic_ast.FunctionDecl:
                return FunctionDeclarationFormatterNode(node)
            case t if t is basic_ast.FunctionDef:
                return FunctionDefinitionFormatterNode(node)
            case t if t is basic_ast.SubroutineDecl:
                return FunctionDeclarationFormatterNode(node)
            case t if t is basic_ast.SubroutineDef:
                return FunctionDefinitionFormatterNode(node)
            case t if t is basic_ast.InitializerList:
                return InitializerListFormatterNode(node)
            case t if t is basic_ast.VariableDecl:
                return VariableDeclFormatterNode(node)
            case t if t is basic_ast.FuncCallOrArrayIndex:
                return FuncCallOrArrayIndexFormatterNode(node)
            case t if t is basic_ast.PrintCall:
                return PrintCallFormatterNode(node)
            case t if t is basic_ast.LenCall:
                return LenCallFormatterNode(node)
            case t if t is basic_ast.FuncCall:
                return FuncCallFormatterNode(node)
            case t if t is basic_ast.ArrayIndex:
                return ArrayIndexFormatterNode(node)
            case t if t is basic_ast.ExitFor:
                return ExitForFormatterNode(node)
            case t if ((t is basic_ast.ExitWhile) or (t is basic_ast.ExitFunction) or (t is basic_ast.ExitSubroutine)):
                return ExitFormatterNode(node)
            case t if t is basic_ast.AssignStatement:
                return AssignStatementFormatterNode(node)
            case t if t is basic_ast.ForLoop:
                return ForLoopFormatterNode(node)
            case t if t is basic_ast.WhileLoop:
                return WhileLoopFormatterNode(node)
            case t if t is basic_ast.IfElseStatement:
                return IfElseFormatterNode(node)
            case t if t is basic_ast.ImplicitTypeCast:
                return ImplicitTypeCastFormatterNode(node)
            case t if t is basic_ast.UnaryOpExpr:
                return UnaryOpFormatterNode(node)
            case t if t is basic_ast.BinOpExpr:
                return BinaryOpFormatterNode(node)
            case t if t is basic_ast.Program:
                return ProgramFormatterNode(node)
        return None

class ConstExprFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.ConstExpr):
        value = str(node.value).replace("\n", "\\n")
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.type}\' \'{value}\'")

class VariableFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.Variable):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.name.name}\' \'{node.type}\'")

class VariableReferenceFormatterNode(VariableFormatterNode):
    def __init__(self, node: basic_ast.VariableReference):
        super().__init__(node)

class ArrayFormatterNode(VariableFormatterNode):
    def __init__(self, node: basic_ast.Array):
        super().__init__(node)

class ArrayReferenceFormatterNode(VariableFormatterNode):
    def __init__(self, node: basic_ast.ArrayReference):
        super().__init__(node)

class CompoundStatementFormatterNode(AstFormatterNode):
    def __init__(self, statements):
        pos = statements[0].pos
        super().__init__(title=f"CompoundStatement <line:{pos.line}, col:{pos.col}>")
        self.statements = statements

    def __len__(self):
        return len(self.statements)

    def __iter__(self):
        for statement in self.statements:
            yield AstFormatterNode.create(statement)

class FunctionDeclarationFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.FunctionDecl):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.proto.name.name}\' \'{node.proto.type}\'")
        self.node = node

    def __len__(self):
        return len(self.node.proto.args)

    def __iter__(self):
        for arg in self.node.proto.args:
            yield AstFormatterNode.create(arg)

class FunctionDefinitionFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.FunctionDef):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.proto.name.name}\' \'{node.proto.type}\'")
        self.node = node

    def __len__(self):
        return len(self.node.proto.args) + 1

    def __iter__(self):
        for arg in self.node.proto.args:
            yield AstFormatterNode.create(arg)
        yield CompoundStatementFormatterNode(self.node.body)

class InitializerListFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.InitializerList):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.type}\'")
        self.node = node

    def __len__(self):
        return len(self.node.values)

    def __iter__(self):
        for value in self.node.values:
            yield AstFormatterNode.create(value)

class VariableDeclFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.VariableDecl):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.variable.name.name}\' \'{node.variable.type}\'")
        self.node = node

    def __len__(self):
        return 0 if self.node.init_value is None else 1

    def __iter__(self):
        if self.node.init_value is not None:
            yield AstFormatterNode.create(self.node.init_value)

class FuncCallOrArrayIndexFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.FuncCallOrArrayIndex=None, title=None):
        if title is not None:
            super().__init__(title=title)
        elif node is not None:
            super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.name.name}\' \'{node.name.type}\'")
        self.node = node

    def __len__(self):
        return len(self.node.args)

    def __iter__(self):
        for arg in self.node.args:
            yield AstFormatterNode.create(arg)

class PrintCallFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.PrintCall):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'PrintCall\'")
        self.node = node

    def __len__(self):
        return len(self.node.args)

    def __iter__(self):
        for arg in self.node.args:
            yield AstFormatterNode.create(arg)

class LenCallFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.LenCall):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'LenCall\'")
        self.node = node

    def __len__(self):
        return 1

    def __iter__(self):
        yield AstFormatterNode.create(self.node.array)

class FuncCallFormatterNode(FuncCallOrArrayIndexFormatterNode):
    def __init__(self, node: basic_ast.FuncCall):
        super().__init__(node=node)

class ArrayIndexFormatterNode(FuncCallOrArrayIndexFormatterNode):
    def __init__(self, node: basic_ast.ArrayIndex):
        super().__init__(node=node,
                         title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.name.name}\' \'{node.type}\'")

class ExitForFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.ExitFor):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}>")
        self.node = node

    def __len__(self):
        return 0 if self.node.name is None else 1

    def __iter__(self):
        if self.node.name is not None:
            yield AstFormatterNode.create(self.node.name)

class ExitFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.ExitStatement):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}>")

class AssignStatementFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.AssignStatement):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.variable.type}\' \'=\'")
        self.node = node

    def __len__(self):
        return 2

    def __iter__(self):
        yield AstFormatterNode.create(self.node.variable)
        yield AstFormatterNode.create(self.node.expr)

class NextFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.Variable):
        super().__init__(title=f"NextStatement <line:{node.pos.line}, col:{node.pos.col}>")
        self.node = node

    def __len__(self):
        return 1

    def __iter__(self):
        yield AstFormatterNode.create(self.node)

class ForLoopRangeFormatterNode(AstFormatterNode):
    def __init__(self, variable: basic_ast.Variable, from_expr: basic_ast.Expr, to_expr: basic_ast.Expr):
        super().__init__(title=f"ForLoopRange <line:{variable.pos.line}, col:{variable.pos.col}> \'{variable.name.name}\' \'{variable.type}\'")
        self.from_expr = from_expr
        self.to_expr = to_expr

    def __len__(self):
        return 2

    def __iter__(self):
        yield AstFormatterNode.create(self.from_expr)
        yield AstFormatterNode.create(self.to_expr)

class ForLoopFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.ForLoop):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}>")
        self.node = node

    def __len__(self):
        return 3

    def __iter__(self):
        yield ForLoopRangeFormatterNode(self.node.variable, self.node.start, self.node.end)
        yield CompoundStatementFormatterNode(self.node.body)
        yield NextFormatterNode(self.node.next)

class WhileLoopFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.WhileLoop):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.type.name}\'")
        self.node = node

    def __len__(self):
        return 2
    def __iter__(self):
        yield AstFormatterNode.create(self.node.condition)
        yield CompoundStatementFormatterNode(self.node.body)

class IfElseFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.IfElseStatement):
        super().__init__(title=
                         f"{type(node).__name__} "
                         f"<line:{node.pos.line}, col:{node.pos.col}> "
                         f"\'{"" if node.else_branch is None else "has_else"}\'")
        self.node = node

    def __len__(self):
        return 2 if (self.node.else_branch is None) or (len(self.node.else_branch) == 0) else 3

    def __iter__(self):
        yield AstFormatterNode.create(self.node.condition)
        yield CompoundStatementFormatterNode(self.node.then_branch)
        if self.node.else_branch is not None and len(self.node.else_branch) != 0:
            yield CompoundStatementFormatterNode(self.node.else_branch)

class ImplicitTypeCastFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.ImplicitTypeCast):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.type}\'")
        self.node = node

    def __len__(self):
        return 1

    def __iter__(self):
        yield AstFormatterNode.create(self.node.expr)

class UnaryOpFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.UnaryOpExpr):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.type}\' \'{node.op}\'")
        self.node = node

    def __len__(self):
        return 1

    def __iter__(self):
        yield AstFormatterNode.create(self.node.unary_expr)

class BinaryOpFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.BinOpExpr):
        super().__init__(title=f"{type(node).__name__} <line:{node.pos.line}, col:{node.pos.col}> \'{node.type}\' \'{node.op}\'")
        self.node = node

    def __len__(self):
        return 2

    def __iter__(self):
        yield AstFormatterNode.create(self.node.left)
        yield AstFormatterNode.create(self.node.right)

class ProgramFormatterNode(AstFormatterNode):
    def __init__(self, node: basic_ast.Program):
        super().__init__(title=f"{type(node).__name__} <line:{0}, col:{0}>")
        self.node = node

    def __len__(self):
        return len(self.node.decls)

    def __iter__(self):
        for decl in self.node.decls:
            yield AstFormatterNode.create(decl)