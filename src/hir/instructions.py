import src.hir.types as hir_types
import src.hir.values as hir_values

class Instruction(hir_values.NamedValue):
    def __init__(self, parent, optype: hir_types.Type, opname, operands, name=""):
        super(Instruction, self).__init__(parent, optype, name)
        self.optype = optype
        self.opname = opname
        self.operands = operands

    def __str__(self):
        return f"{self.opname} {self.optype} {', '.join(map(str, self.operands))}\n"

class CallInstruction(Instruction):
    def __init__(self, parent, func, args, name=""):
        super(CallInstruction, self).__init__(parent, func.function_type.return_type, "call", [func] + list(args), name=name)

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

class CompareInstruction(Instruction):
    # Define the following in subclasses
    OPNAME = 'invalid-compare'
    VALID_OP = {}

    def __init__(self, parent, op, lhs, rhs, name=''):
        if op not in self.VALID_OP:
            raise ValueError("invalid comparison %r for %s" % (op, self.OPNAME))
        opname = self.OPNAME
        super(CompareInstruction, self).__init__(parent, hir_types.BoolType(), opname, [lhs, rhs], name=name)
        self.op = op

    def __str__(self):
        return "{opname} {op} {ty} {lhs}, {rhs}\n".format(
            opname=self.opname,
            op=self.op,
            ty=self.operands[0].type,
            lhs=self.operands[0].get_reference(),
            rhs=self.operands[1].get_reference(),
        )

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

class StoreInstruction(Instruction):
    def __init__(self, parent, value, ptr):
        super(StoreInstruction, self).__init__(parent, hir_types.VoidType(), "store", [value, ptr])

class CopyInstruction(Instruction):
    def __init__(self, parent, dest, src, size):
        super(CopyInstruction, self).__init__(parent, hir_types.VoidType(), "copy", [dest, src, size])

class AllocateInstruction(Instruction):
    def __init__(self, parent, typ, count, name):
        operands = [count] if count else ()
        super(AllocateInstruction, self).__init__(parent, hir_types.PointerType(), "alloca", operands, name)
        self.allocated_type = typ
        self.align = None

class GEPInstruction(Instruction):
    def __init__(self, parent, type, ptr, indices, name):
        super(GEPInstruction, self).__init__(parent, type, "getelementptr", [ptr] + list(indices), name=name)
        self.pointer = ptr
        self.indices = indices

class PhiInstruction(Instruction):
    def __init__(self, parent, typ, name):
        super(PhiInstruction, self).__init__(parent, typ, "phi", (), name=name)
        self.incomings = []

    def add_incoming(self, value, block):
        assert isinstance(block, hir_values.Block)
        self.incomings.append((value, block))




