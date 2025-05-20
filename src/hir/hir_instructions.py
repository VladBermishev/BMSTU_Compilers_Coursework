import src.hir.hir_types as hir_types

class Instruction:
    def __init__(self, optype, opname, operands):
        self.optype = optype
        self.opname = opname
        self.operands = operands

    def __str__(self):
        return f"{self.opname} {self.optype} {', '.join(map(str, self.operands))}\n"

class CallInstruction(Instruction):
    pass

class Terminator(Instruction):
    def __init__(self, opname, operands):
        super(Terminator, self).__init__(hir_types.VoidType(), opname, operands)

    def __str__(self):
        operands = ', '.join(["{0} {1}".format(op.type, op.get_reference()) for op in self.operands])
        return f"{self.opname} {operands}"

class ReturnInstruction(Terminator):
    def __init__(self, opname, return_value=None):
        operands = [return_value] if return_value is not None else []
        super(ReturnInstruction, self).__init__(opname, operands)

class BranchInstruction(Terminator):
    def __init__(self, label):
        super(Terminator, self).__init__(hir_types.VoidType(), "br", [label])

class ConditionalBranchInstruction(Terminator):
    def __init__(self, cond, lhs, rhs):
        super(Terminator, self).__init__(hir_types.VoidType(), "br", [cond, lhs, rhs])

class SelectInstruction(Instruction):
    def __init__(self, cond, lhs, rhs):
        super(SelectInstruction, self).__init__(lhs.type, "select", [cond, lhs, rhs])

class CompareInstruction(Instruction):
    pass

class IntCompareInstruction(CompareInstruction):
    pass

class FloatCompareInstruction(CompareInstruction):
    pass

class CastInstr(Instruction):
    def __init__(self, op, val, typ):
        super(CastInstr, self).__init__(typ, op, [val])

class LoadInstruction(Instruction):
    def __init__(self, ptr, load_type):
        super(LoadInstruction, self).__init__(load_type, "load", [ptr])

class StoreInstruction(Instruction):
    def __init__(self, value, ptr):
        super(StoreInstruction, self).__init__(hir_types.VoidType(), "store", [value, ptr])

class AllocateInstruction(Instruction):
    pass

class GEPInstruction(Instruction):
    pass

class PhiInstr(Instruction):
    pass




