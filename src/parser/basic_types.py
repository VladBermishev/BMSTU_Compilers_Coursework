import enum
from llvmlite import ir


class Type:
    name = "undefined"
    mangle_suff = "Und"

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __ne__(self, other):
        return not self.__eq__(other)

    def default_value(self):
        return None

    def castable_to(self, other_type):
        raise NotImplementedError()

    def cast_to(self, other_type, builder: ir.IRBuilder):
        raise NotImplementedError()

    def __str__(self):
        return "Auto"

    def llvm_type(self):
        pass


class VoidT(Type):
    name = "void"
    mangle_name = ""

    def __str__(self):
        return "void"

    def castable_to(self, other_type):
        return True

    def llvm_type(self) -> ir.VoidType:
        return ir.VoidType()


class NumericT(Type):
    name = "numeric"
    mangle_suff = "N"
    priority = 0

    def default_value(self):
        return 0

    def castable_to(self, other_type):
        return isinstance(other_type, NumericT) and self.priority <= other_type.priority

    def cmp(self, op, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("cmp for NumericT")

    def add(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("add for NumericT")

    def sub(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("sub for NumericT")

    def mul(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("mul for NumericT")

    def div(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("div for NumericT")

    def neg(self, builder: ir.IRBuilder, name: str = None):
        raise NotImplementedError("neg for NumericT")


class IntegralT(NumericT):
    name = "integral"
    mangle_suff = "N"
    priority = 0

    def cast_to(self, other_type, builder: ir.IRBuilder):
        if isinstance(other_type, IntegralT):
            return lambda x: builder.zext(x, other_type.llvm_type())
        elif isinstance(other_type, FloatingPointT):
            return lambda x: builder.sitofp(x, other_type.llvm_type())
        else:
            return None

    def cmp(self, op, builder: ir.IRBuilder, name: str = None):
        op = "!=" if op == "<>" else op
        op = "==" if op == "=" else op
        return lambda lhs, rhs: builder.icmp_signed(op, lhs, rhs, name if name else '')

    def add(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.add(lhs, rhs, name if name else '')

    def sub(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.sub(lhs, rhs, name if name else '')

    def mul(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.mul(lhs, rhs, name if name else '')

    def div(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.sdiv(lhs, rhs, name if name else '')

    def neg(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs: builder.neg(lhs, name if name else '')


class FloatingPointT(NumericT):
    name = "floating_point"
    mangle_suff = "N"
    priority = 0

    def cast_to(self, other_type, builder: ir.IRBuilder):
        if isinstance(other_type, FloatingPointT):
            return lambda x: builder.fpext(x, other_type.llvm_type())
        else:
            return None

    def cmp(self, op, builder: ir.IRBuilder, name: str = None):
        op = "!=" if op == "<>" else op
        op = "==" if op == "=" else op
        return lambda lhs, rhs: builder.fcmp_ordered(op, lhs, rhs, name if name else '')

    def add(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fadd(lhs, rhs, name if name else '')

    def sub(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fsub(lhs, rhs, name if name else '')

    def mul(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fmul(lhs, rhs, name if name else '')

    def div(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs, rhs: builder.fdiv(lhs, rhs, name if name else '')

    def neg(self, builder: ir.IRBuilder, name: str = None):
        return lambda lhs: builder.fneg(lhs, name if name else '')


class BoolT(IntegralT):
    name = "bool"
    mangle_suff = "B"
    priority = 1

    def __str__(self):
        return "Bool"

    def llvm_type(self):
        return ir.IntType(8)


class IntegerT(IntegralT):
    name = "%"
    mangle_suff = "I"
    priority = 2

    def __str__(self):
        return "Integer"

    def llvm_type(self):
        return ir.IntType(32)


class LongT(IntegralT):
    name = "&"
    mangle_suff = "L"
    priority = 3

    def __str__(self):
        return "Long"

    def llvm_type(self):
        return ir.IntType(64)


class FloatT(FloatingPointT):
    name = "!"
    mangle_suff = "F"
    priority = 4

    def __str__(self):
        return "Float"

    def llvm_type(self):
        return ir.FloatType()


class DoubleT(FloatingPointT):
    name = "#"
    mangle_suff = "D"
    priority = 5

    def __str__(self):
        return "Double"

    def llvm_type(self):
        return ir.DoubleType()


class StringT(Type):
    name = "$"
    mangle_suff = "S"
    priority = 0

    def __init__(self, is_const:bool = False, len:int = 0):
        super().__init__()
        self.is_const = is_const
        self.len = len


    def __str__(self):
        return "String"

    def default_value(self):
        if self.is_const:
            return bytearray([0] * ((self.len + 1) * 4))
        else:
            return None

    def castable_to(self, other_type):
        return isinstance(other_type, StringT)

    def cast_to(self, other_type, builder: ir.IRBuilder):
        pass

    def llvm_type(self):
        if self.is_const:
            return ir.ArrayType(ir.IntType(32), self.len + 1)
        else:
            return ir.PointerType(ir.IntType(32))


class ArrayT(Type):
    name = "array"

    def __init__(self, valueT:Type, size: list[int], is_function_param: bool = False):
        self.type = valueT
        self.size = size
        self.mangle_suff = "A" + valueT.mangle_suff * len(size)
        self.is_function_param = is_function_param

    def __eq__(self, other):
        if isinstance(other, ArrayT):
            self_any = self.type == Type()
            other_any = other.type == Type()
            if self_any or other_any:
                return self.size == other.size if len(self.size) != 1 and len(other.size) != 1 else True
            if isinstance(self.size[0], int) and isinstance(other.size[0], int) and self.is_function_param == other.is_function_param:
                return self.type == other.type and self.size == other.size
            else:
                return self.type == other.type and len(self.size) == len(other.size)
        return False

    def __str__(self):
        return f"{self.type}[]"

    def default_value(self):
        sz = self.size[0] if not hasattr(self.size[0], "value") else self.size[0].value
        if len(self.size) == 1:
            return [0] * sz
        elif len(self.size) >= 1:
            return [ArrayT(self.type, self.size[1:]).default_value()] * sz


    def llvm_type(self):
        if self.is_function_param:
            return self.llvm_type_ref()
        else:
            return self.llvm_type_init()

    def llvm_type_init(self):
        if len(self.size) == 1:
            return ir.ArrayType(self.type.llvm_type(), self.size[0])
        elif len(self.size) >= 1:
            return ir.ArrayType(ArrayT(self.type, self.size[1:]).llvm_type_init(), self.size[0])

    def llvm_type_ref(self):
        if len(self.size) == 1:
            return ir.PointerType(self.type.llvm_type(), self.size[0])
        elif len(self.size) >= 1:
            return ir.PointerType(ArrayT(self.type, self.size[1:]).llvm_type_ref(), self.size[0])

    def cast_to(self, other_type, builder: ir.IRBuilder):
        def casting(lhs_val_list, rhs_val_list):
            result = []
            for lhs_val, rhs_val in zip(lhs_val_list, rhs_val_list):
                result.append(self.type.cast_to(other_type, builder)(lhs_val, rhs_val))
            return result
        return casting

    def castable_to(self, other_type):
        return self.size == other_type.size and self.type == other_type.type


class VariadicArgumentT(Type):
    name = "..."

    def __str__(self):
        return self.name


class ProcedureT(Type):
    name = "proc"

    def __init__(self, retT: Type, argsT: list[Type]):
        self.retT = retT
        self.argsT = argsT

    def __eq__(self, other):
        if isinstance(other, ProcedureT):
            va_lhs = sum(1 if isinstance(arg, VariadicArgumentT) else 0 for arg in self.argsT)
            va_rhs = sum(1 if isinstance(arg, VariadicArgumentT) else 0 for arg in other.argsT)
            if va_lhs > 0 or va_rhs > 0:
                result = True
                for idx in range(min(len(self.argsT), len(other.argsT))):
                    if isinstance(self.argsT[idx],  VariadicArgumentT) or isinstance(other.argsT[idx],  VariadicArgumentT):
                        return result
                    result &= self.argsT[idx] == other.argsT[idx]
                return result
            else:
                result = self.retT == other.retT and len(self.argsT) == len(other.argsT)
                return result and all([self.argsT[i] == other.argsT[i] for i in range(len(self.argsT))])
        return False

    def __str__(self):
        return f"{self.retT}(" + ','.join([str(v) for v in self.argsT]) + ")"

    def castable_to(self, other_type):
        result = self.retT == other_type.retT and len(self.argsT) == len(other_type.argsT)
        if not result:
            return False
        for idx in range(len(self.argsT)):
            result &= self.argsT[idx].castable_to(other_type.argsT[idx])
        return result


class WhileType(enum.Enum):
    Endless = 0
    PreUntil = 1
    PreWhile = 2
    PostUntil = 3
    PostWhile = 4
