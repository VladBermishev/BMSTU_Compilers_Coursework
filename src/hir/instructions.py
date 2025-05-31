import copy
import src.hir.types as hir_types
import src.hir.values as hir_values

class Instruction(hir_values.NamedValue):
    def __init__(self, parent, optype: hir_types.Type, opname, operands, name=hir_values.NamedValue.empty_name):
        super(Instruction, self).__init__(parent, optype, name)
        self.optype = optype
        self.opname = opname
        self.operands = operands

    def __str__(self):
        if self.name != hir_values.NamedValue.empty_name:
            return f"{self.get_reference()} = {self.opname} {self.optype} {', '.join([x.get_reference() for x in self.operands])}"
        return f"{self.opname} {self.optype} {', '.join(map(str, self.operands))}"

    def replace_oper(self, old, new):
        if old in self.operands:
            ops = []
            for oper in self.operands:
                ops.append(new if oper is old else oper)
            self.operands = ops

class CallInstruction(Instruction):
    def __init__(self, parent, func, args, name=""):
        if isinstance(func.ftype.return_type, hir_types.VoidType):
            super(CallInstruction, self).__init__(parent, func.ftype.return_type, "call", [func] + list(args))
        else:
            super(CallInstruction, self).__init__(parent, func.ftype.return_type, "call", [func] + list(args), name=name)

    @property
    def callee(self):
        return self.operands[0]

    @callee.setter
    def callee(self, newcallee):
        self.operands[0] = newcallee

    @property
    def args(self):
        return self.operands[1:]

    def __str__(self):
        args = ', '.join([f'{a.type} {a.get_reference()}' for a in self.args])
        fnty = self.callee.ftype
        callee_ref = "{0} {1}".format(fnty.return_type, self.callee.get_reference())
        if self.name != hir_values.NamedValue.empty_name:
            return f"{self.get_reference()} = {self.opname} {callee_ref}({args})"
        else:
            return f"{self.opname} {callee_ref}({args})"

class Terminator(Instruction):
    def __init__(self, parent, opname, operands):
        super(Terminator, self).__init__(parent, hir_types.VoidType(), opname, operands)

    def __str__(self):
        operands = ', '.join(["{0} {1}".format(op.type, op.get_reference()) for op in self.operands])
        return f"{self.opname} {operands}"

class ReturnInstruction(Terminator):
    def __init__(self, parent, opname, return_value=None):
        operands = [return_value] if return_value is not None else []
        super(ReturnInstruction, self).__init__(parent, opname, operands)

class BranchInstruction(Terminator):
    def __init__(self, parent, label):
        super(Terminator, self).__init__(parent, hir_types.VoidType(), "br", [label])

class ConditionalBranchInstruction(Terminator):
    def __init__(self, parent, cond, lhs, rhs):
        super(Terminator, self).__init__(parent, hir_types.VoidType(), "br", [cond, lhs, rhs])

class SelectInstruction(Instruction):
    def __init__(self, parent, cond, lhs, rhs, name=""):
        super(SelectInstruction, self).__init__(parent, lhs.type, "select", [cond, lhs, rhs], name=name)

    def is_related(self, other):
        if isinstance(other, SelectInstruction):
            return self.operands[0].is_related(other.operands[0])
        return False

class CompareInstruction(Instruction):
    # Define the following in subclasses
    OPNAME = 'invalid-compare'
    VALID_OP = {}
    INVERSE_OP = {
        'eq': 'ne',
        'ne': 'eq',
        'slt': 'sge',
        'sle': 'sgt',
        'sgt': 'sle',
        'sge': 'slt',
        'ult': 'uge',
        'ule': 'ugt',
        'ugt': 'ule',
        'uge': 'ult',
        'false': 'true',
        'oeq': 'one',
        'ogt': 'ole',
        'oge': 'olt',
        'olt': 'oge',
        'ole': 'ogt',
        'one': 'oeq',
        'ord': 'uno',
        'ueq': 'une',
        'ugt': 'ule',
        'uge': 'ult',
        'ult': 'uge',
        'ule': 'ugt',
        'une': 'ueq',
        'uno': 'ord',
        'true': 'false',
    }
    OP_MAP = {
        'eq': '==',
        'ne': '!=',
        'lt': '<',
        'le': '<=',
        'gt': '>',
        'ge': '>=',
    }

    def __init__(self, parent, op, lhs, rhs, name=''):
        if op not in self.VALID_OP:
            raise ValueError("invalid comparison %r for %s" % (op, self.OPNAME))
        opname = self.OPNAME
        super(CompareInstruction, self).__init__(parent, hir_types.BoolType(), opname, [lhs, rhs], name=name)
        self.op = op

    def __str__(self):
        return "{name} = {opname} {op} {ty} {lhs}, {rhs}".format(
            name = self.get_reference(),
            opname=self.opname,
            op=self.op,
            ty=self.operands[0].type,
            lhs=self.operands[0].get_reference(),
            rhs=self.operands[1].get_reference(),
        )

    def is_identical(self, other):
        if isinstance(other, CompareInstruction):
            return (
                    self.opname == other.opname and
                    (self.op == other.op) and
                    all([lhs == rhs for lhs, rhs in zip(self.operands, other.operands)])
            )
        return False

    def is_related(self, other):
        if isinstance(other, CompareInstruction):
            return (
                    self.opname == other.opname and
                    (self.op == other.op or self.op == self.INVERSE_OP[other.op]) and
                    all([lhs == rhs for lhs, rhs in zip(self.operands, other.operands)])
            )
        return False

class IntCompareInstruction(CompareInstruction):
    OPNAME = 'icmp'
    VALID_OP = {
        'eq': 'equal',
        'ne': 'not equal',
        'ugt': 'unsigned greater than',
        'uge': 'unsigned greater or equal',
        'ult': 'unsigned less than',
        'ule': 'unsigned less or equal',
        'sgt': 'signed greater than',
        'sge': 'signed greater or equal',
        'slt': 'signed less than',
        'sle': 'signed less or equal',
    }

class FloatCompareInstruction(CompareInstruction):
    OPNAME = 'fcmp'
    VALID_OP = {
        'false': 'no comparison, always returns false',
        'oeq': 'ordered and equal',
        'ogt': 'ordered and greater than',
        'oge': 'ordered and greater than or equal',
        'olt': 'ordered and less than',
        'ole': 'ordered and less than or equal',
        'one': 'ordered and not equal',
        'ord': 'ordered (no nans)',
        'ueq': 'unordered or equal',
        'ugt': 'unordered or greater than',
        'uge': 'unordered or greater than or equal',
        'ult': 'unordered or less than',
        'ule': 'unordered or less than or equal',
        'une': 'unordered or not equal',
        'uno': 'unordered (either nans)',
        'true': 'no comparison, always returns true',
    }

class CastInstruction(Instruction):
    def __init__(self, parent, op, val, typ, name):
        super(CastInstruction, self).__init__(parent, typ, op, [val], name=name)

class LoadInstruction(Instruction):
    def __init__(self, parent, ptr, load_type, name):
        super(LoadInstruction, self).__init__(parent, load_type, "load", [ptr], name=name)

    def __str__(self):
        [val] = self.operands
        return "{0} = load {1}, {2} {3}".format(
            self.get_reference(),
            self.type,
            val.type,
            val.get_reference(),
        )

class StoreInstruction(Instruction):
    def __init__(self, parent, value, ptr):
        assert value is not None
        super(StoreInstruction, self).__init__(parent, hir_types.VoidType(), "store", [value, ptr])

    def __str__(self):
        val, ptr = self.operands
        return "store {0} {1}, {2} {3}".format(
            val.type,
            val.get_reference(),
            ptr.type,
            ptr.get_reference(),
        )

class CopyInstruction(Instruction):
    def __init__(self, parent, dest, src, size):
        super(CopyInstruction, self).__init__(parent, hir_types.VoidType(), "copy", [dest, src, size])
    @property
    def size(self):
        return self.operands[2]

    def __str__(self):
        dest, src, sz = self.operands
        return "copy {0} {1}, {2} {3}, {4}".format(
            dest.type,
            dest.get_reference(),
            src.type,
            src.get_reference(),
            sz,
        )

class AllocateInstruction(Instruction):
    def __init__(self, parent, typ, count, name):
        operands = [count] if count else ()
        super(AllocateInstruction, self).__init__(parent, hir_types.PointerType(), "alloca", operands, name)
        self.allocated_type = typ
        self.align = None

    def __str__(self):
        result = f"{self.get_reference()} = {self.opname} {self.allocated_type}"
        if self.operands:
            op, = self.operands
            result += f", {op}"
        return result

class GEPInstruction(Instruction):
    def __init__(self, parent, type, ptr, indices, name):
        super(GEPInstruction, self).__init__(parent, ptr.type, "getelementptr", [ptr] + list(indices), name=name)
        self.source_etype = type

    def __str__(self):
        indices = ['{0} {1}'.format(i.type, i.get_reference()) for i in self.operands[1:]]
        return "{0} = getelementptr {1}, {2} {3}, {4}".format(
            self.get_reference(),
            self.source_etype,
            self.operands[0].type,
            self.operands[0].get_reference(),
            ', '.join(indices),
        )


class PhiInstruction(Instruction):
    def __init__(self, parent, typ, name=""):
        super(PhiInstruction, self).__init__(parent, typ, "phi", (), name=name)
        self.incomings = []
        self.metadata = None

    def add_incoming(self, value, block):
        assert isinstance(block, hir_values.Block)
        self.incomings.append((value, block))

    def replace_oper(self, old, new):
        if old in [inc[0] for inc in self.incomings]:
            self.incomings = [(new if val is old else val, block) for val, block in self.incomings]

    def replace_block(self, old, new):
        if old in [inc[0] for inc in self.incomings]:
            self.incomings = [(val, new if block is old else block) for val, block in self.incomings]

    def __str__(self):
        incs = ', '.join('[{0}, {1}]'.format(v.get_reference(), b.get_reference()) for v, b in self.incomings)
        return f"{self.get_reference()} = phi {self.type} {incs}"



