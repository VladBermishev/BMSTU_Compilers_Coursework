import functools
import src.hir.instructions as hir_instructions
import src.hir.values as hir_values
import src.hir.types as hir_types

_CMP_MAP = {
    '>': 'gt',
    '<': 'lt',
    '==': 'eq',
    '!=': 'ne',
    '>=': 'ge',
    '<=': 'le',
}

def _unary_operation(opname, cls=hir_instructions.Instruction):
    def wrap(fn):
        @functools.wraps(fn)
        def wrapped(self, arg, name=''):
            instr = cls(self.block, arg.type, opname, [arg], name)
            self._insert(instr)
            return instr

        return wrapped

    return wrap

def _binary_operation(opname, cls=hir_instructions.Instruction):
    def wrap(fn):
        @functools.wraps(fn)
        def wrapped(self, lhs, rhs, name=''):
            if lhs.type != rhs.type:
                raise ValueError("Operands must be the same type, got (%s, %s)"
                                 % (lhs.type, rhs.type))
            instr = cls(self.block, lhs.type, opname, (lhs, rhs), name)
            self._insert(instr)
            return instr

        return wrapped

    return wrap

def _castop(opname, cls=hir_instructions.CastInstruction):
    def wrap(fn):
        @functools.wraps(fn)
        def wrapped(self, val, typ, name=''):
            if val.type == typ:
                return val
            instr = cls(self.block, opname, val, typ, name)
            self._insert(instr)
            return instr

        return wrapped

    return wrap


class HirBuilder:
    def __init__(self, block=None):
        self.block = block
        self._instruction_index = 0
        self.position_at_end(block)

    def position_before(self, instr):
        """
        Position immediately before the given instruction.  The current block
        is also changed to the instruction's basic block.
        """
        self.block = instr.parent
        self._instruction_index = self.block.instructions.index(instr)

    def position_after(self, instr):
        """
        Position immediately after the given instruction.  The current block
        is also changed to the instruction's basic block.
        """
        self.block = instr.parent
        self._instruction_index = self.block.instructions.index(instr) + 1

    def position_at_start(self, block):
        """
        Position at the start of the basic *block*.
        """
        self.block = block
        self._instruction_index = 0

    def position_at_end(self, block):
        self.block = block
        self._instruction_index = len(block.instructions)

    def _insert(self, instr):
        self.block.instructions.insert(self._instruction_index, instr)
        self._instruction_index += 1

    def _set_terminator(self, term):
        assert not self.block.is_terminated
        self._insert(term)
        self.block.terminator = term
        return term

    @_binary_operation('shl')
    def shl(self, lhs, rhs, name=''):
        """
        Left integer shift:
            name = lhs << rhs
        """

    @_binary_operation('lshr')
    def lshr(self, lhs, rhs, name=''):
        """
        Logical (unsigned) right integer shift:
            name = lhs >> rhs
        """

    @_binary_operation('ashr')
    def ashr(self, lhs, rhs, name=''):
        """
        Arithmetic (signed) right integer shift:
            name = lhs >> rhs
        """

    @_binary_operation('add')
    def add(self, lhs, rhs, name=''):
        """
        Integer addition:
            name = lhs + rhs
        """

    @_binary_operation('fadd')
    def fadd(self, lhs, rhs, name=''):
        """
        Floating-point addition:
            name = lhs + rhs
        """

    @_binary_operation('sub')
    def sub(self, lhs, rhs, name=''):
        """
        Integer subtraction:
            name = lhs - rhs
        """

    @_binary_operation('fsub')
    def fsub(self, lhs, rhs, name=''):
        """
        Floating-point subtraction:
            name = lhs - rhs
        """

    @_binary_operation('mul')
    def mul(self, lhs, rhs, name=''):
        """
        Integer multiplication:
            name = lhs * rhs
        """

    @_binary_operation('fmul')
    def fmul(self, lhs, rhs, name=''):
        """
        Floating-point multiplication:
            name = lhs * rhs
        """

    @_binary_operation('udiv')
    def udiv(self, lhs, rhs, name=''):
        """
        Unsigned integer division:
            name = lhs / rhs
        """

    @_binary_operation('sdiv')
    def sdiv(self, lhs, rhs, name=''):
        """
        Signed integer division:
            name = lhs / rhs
        """

    @_binary_operation('fdiv')
    def fdiv(self, lhs, rhs, name=''):
        """
        Floating-point division:
            name = lhs / rhs
        """

    @_binary_operation('urem')
    def urem(self, lhs, rhs, name=''):
        """
        Unsigned integer remainder:
            name = lhs % rhs
        """

    @_binary_operation('srem')
    def srem(self, lhs, rhs, name=''):
        """
        Signed integer remainder:
            name = lhs % rhs
        """

    @_binary_operation('frem')
    def frem(self, lhs, rhs, name=''):
        """
        Floating-point remainder:
            name = lhs % rhs
        """

    @_binary_operation('or')
    def or_(self, lhs, rhs, name=''):
        """
        Bitwise integer OR:
            name = lhs | rhs
        """

    @_binary_operation('and')
    def and_(self, lhs, rhs, name=''):
        """
        Bitwise integer AND:
            name = lhs & rhs
        """

    @_binary_operation('xor')
    def xor(self, lhs, rhs, name=''):
        """
        Bitwise integer XOR:
            name = lhs ^ rhs
        """

    def not_(self, value, name=''):
        """
        Bitwise integer complement:
            name = ~value
        """
        return self.xor(value, hir_values.ConstantValue(value.type, -1), name=name)

    def neg(self, value, name=''):
        """
        Integer negative:
            name = -value
        """
        return self.sub(hir_values.ConstantValue(value.type, 0), value, name=name)

    @_unary_operation('fneg')
    def fneg(self, arg, name='', flags=()):
        """
        Floating-point negative:
            name = -arg
        """

    #
    # Comparison APIs
    #

    def _icmp(self, prefix, cmpop, lhs, rhs, name):
        try:
            op = _CMP_MAP[cmpop]
        except KeyError:
            raise ValueError("invalid comparison %r for icmp" % (cmpop,))
        if cmpop not in ('==', '!='):
            op = prefix + op
        instr = hir_instructions.IntCompareInstruction(self.block, op, lhs, rhs, name=name)
        self._insert(instr)
        return instr

    def icmp_signed(self, cmpop, lhs, rhs, name=''):
        """
        Signed integer comparison:
            name = lhs <cmpop> rhs

        where cmpop can be '==', '!=', '<', '<=', '>', '>='
        """
        return self._icmp('s', cmpop, lhs, rhs, name)

    def icmp_unsigned(self, cmpop, lhs, rhs, name=''):
        """
        Unsigned integer (or pointer) comparison:
            name = lhs <cmpop> rhs

        where cmpop can be '==', '!=', '<', '<=', '>', '>='
        """
        return self._icmp('u', cmpop, lhs, rhs, name)

    def fcmp_ordered(self, cmpop, lhs, rhs, name=''):
        """
        Floating-point ordered comparison:
            name = lhs <cmpop> rhs

        where cmpop can be '==', '!=', '<', '<=', '>', '>=', 'ord', 'uno'
        """
        if cmpop in _CMP_MAP:
            op = 'o' + _CMP_MAP[cmpop]
        else:
            op = cmpop
        instr = hir_instructions.FloatCompareInstruction(self.block, op, lhs, rhs, name=name)
        self._insert(instr)
        return instr

    def fcmp_unordered(self, cmpop, lhs, rhs, name=''):
        """
        Floating-point unordered comparison:
            name = lhs <cmpop> rhs

        where cmpop can be '==', '!=', '<', '<=', '>', '>=', 'ord', 'uno'
        """
        if cmpop in _CMP_MAP:
            op = 'u' + _CMP_MAP[cmpop]
        else:
            op = cmpop
        instr = hir_instructions.FloatCompareInstruction(self.block, op, lhs, rhs, name=name)
        self._insert(instr)
        return instr

    def select(self, cond, lhs, rhs, name=''):
        """
        Ternary select operator:
            name = cond ? lhs : rhs
        """
        instr = hir_instructions.SelectInstruction(self.block, cond, lhs, rhs, name=name)
        self._insert(instr)
        return instr

    #
    # Cast APIs
    #

    @_castop('trunc')
    def trunc(self, value, typ, name=''):
        """
        Truncating integer downcast to a smaller type:
            name = (typ) value
        """

    @_castop('zext')
    def zext(self, value, typ, name=''):
        """
        Zero-extending integer upcast to a larger type:
            name = (typ) value
        """

    @_castop('sext')
    def sext(self, value, typ, name=''):
        """
        Sign-extending integer upcast to a larger type:
            name = (typ) value
        """

    @_castop('fptrunc')
    def fptrunc(self, value, typ, name=''):
        """
        Floating-point downcast to a less precise type:
            name = (typ) value
        """

    @_castop('fpext')
    def fpext(self, value, typ, name=''):
        """
        Floating-point upcast to a more precise type:
            name = (typ) value
        """

    def alloca(self, typ, size=None, name=''):
        """
        Stack-allocate a slot for *size* elements of the given type.
        (default one element)
        """
        if size is None:
            pass
        elif isinstance(size, (hir_values.Value, hir_values.ConstantValue)):
            assert isinstance(size.type, (hir_types.IntType, hir_types.LongType))
        else:
            size = hir_values.ConstantValue(hir_types.IntType(), size)

        al = hir_instructions.AllocateInstruction(self.block, typ, size, name)
        self._insert(al)
        return al

    def load(self, ptr, name='', typ=None):
        """
        Load value from pointer, with optional guaranteed alignment:
            name = *ptr
        """
        if not isinstance(ptr.type, hir_types.PointerType):
            msg = "cannot load from value of type %s (%r): not a pointer"
            raise TypeError(msg % (ptr.type, str(ptr)))
        ld = hir_instructions.LoadInstruction(self.block, ptr, typ, name)
        self._insert(ld)
        return ld

    def store(self, value, ptr):
        """
        Store value to pointer, with optional guaranteed alignment:
            *ptr = name
        """
        if not isinstance(ptr.type, hir_types.PointerType):
            msg = "cannot store to value of type %s (%r): not a pointer"
            raise TypeError(msg % (ptr.type, str(ptr)))
        st = hir_instructions.StoreInstruction(self.block, value, ptr)
        self._insert(st)
        return st

    def branch(self, target):
        """
        Unconditional branch to *target*.
        """
        br = hir_instructions.BranchInstruction(self.block, target)
        self._set_terminator(br)
        return br

    def cbranch(self, cond, truebr, falsebr):
        """
        Conditional branch to *truebr* if *cond* is true, else to *falsebr*.
        """
        br = hir_instructions.ConditionalBranchInstruction(self.block, cond, truebr, falsebr)
        self._set_terminator(br)
        return br

    def ret_void(self):
        """
        Return from function without a value.
        """
        return self._set_terminator(hir_instructions.ReturnInstruction(self.block, "ret void"))

    def ret(self, value):
        """
        Return from function with the given *value*.
        """
        return self._set_terminator(hir_instructions.ReturnInstruction(self.block, "ret", value))

    # Call APIs

    def call(self, fn, args, name=''):
        """
        Call function *fn* with *args*:
            name = fn(args...)
        """
        inst = hir_instructions.CallInstruction(self.block, fn, args, name=name)
        self._insert(inst)
        return inst

    def gep(self, source_etype, ptr, indices, name=''):
        """
        Compute effective address (getelementptr):
            name = getelementptr ptr, <indices...>
        """
        instr = hir_instructions.GEPInstruction(self.block, source_etype, ptr, indices, name=name)
        self._insert(instr)
        return instr

    def phi(self, typ, name=''):
        inst = hir_instructions.PhiInstruction(self.block, typ, name=name)
        self._insert(inst)
        return inst
