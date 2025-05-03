import enum
import typing


class WhileType(enum.Enum):
    Endless = 0
    PreUntil = 1
    PreWhile = 2
    PostUntil = 3
    PostWhile = 4


class Type:
    name = "undefined"
    mangle_suff = "Und"

    def __eq__(self, other):
        return isinstance(other, type(self))

    def __ne__(self, other):
        return not self.__eq__(other)

    def default_value(self):
        return None

    def __str__(self):
        return "Auto"


class ConstantT(Type):
    name = "constant"


class VoidT(Type):
    name = "void"
    mangle_name = ""

    def __str__(self):
        return "void"

class CharT(Type):
    name = "char"
    mangle_name = "C"

class NumericT(Type):
    name = "numeric"
    mangle_suff = "N"
    priority = 0

    def default_value(self):
        return 0


class IntegralT(NumericT):
    name = "integral"
    mangle_suff = "N"
    priority = 0


class FloatingPointT(NumericT):
    name = "floating_point"
    mangle_suff = "N"
    priority = 0


class BoolT(IntegralT):
    name = "bool"
    mangle_suff = "B"
    priority = 1

    def __str__(self):
        return "Bool"


class IntegerT(IntegralT):
    name = "%"
    mangle_suff = "I"
    priority = 2

    def __str__(self):
        return "Integer"


class LongT(IntegralT):
    name = "&"
    mangle_suff = "L"
    priority = 3

    def __str__(self):
        return "Long"


class FloatT(FloatingPointT):
    name = "!"
    mangle_suff = "F"
    priority = 4

    def __str__(self):
        return "Float"


class DoubleT(FloatingPointT):
    name = "#"
    mangle_suff = "D"
    priority = 5

    def __str__(self):
        return "Double"


class ArrayT(Type):
    name = "array"

    def __init__(self, valueT: Type, size: list[int]):
        self.value_type = valueT
        self.size = size
        self.mangle_suff = "A" + valueT.mangle_suff * len(size)

    def __eq__(self, other):
        if isinstance(other, ArrayT):
            self_any = self.value_type == Type()
            other_any = other.value_type == Type()
            if self_any or other_any:
                return self.size == other.size if len(self.size) != 1 and len(other.size) != 1 else True
            if (isinstance(self.size[0], int) and isinstance(other.size[0], int) and
                    self.is_function_param == other.is_function_param):
                return self.value_type == other.value_type and self.size == other.size
            else:
                return self.value_type == other.value_type and len(self.size) == len(other.size)
        return False

    def __str__(self):
        return f"{self.value_type}[]"

    def default_value(self):
        sz = self.size[0] if not hasattr(self.size[0], "value") else self.size[0].value
        if len(self.size) == 1:
            return [0] * sz
        elif len(self.size) >= 1:
            return [ArrayT(self.value_type, self.size[1:]).default_value()] * sz


class StringT(ArrayT):
    name = "string"
    mangle_suff = "S"

    def __init__(self, length=0):
        super().__init__(CharT(), [length])


class PointerT(Type):
    name = "pointer"

    def __init__(self, valueT: Type):
        self.type = valueT
        self.mangle_suff = f"Ptr{{{valueT.mangle_suff}}}"


class ProcedureT(Type):
    name = "proc"

    def __init__(self, retT: Type, argsT: list[Type]):
        self.retT = retT
        self.argsT = argsT

    def __eq__(self, other):
        if not isinstance(other, ProcedureT):
            return False
        result = self.retT == other.retT and len(self.argsT) == len(other.argsT)
        return result and all([self.argsT[i] == other.argsT[i] for i in range(len(self.argsT))])

    def __str__(self):
        return f"{self.retT}(" + ','.join([str(v) for v in self.argsT]) + ")"


def __unroll_type_tree(tp: Type):
    result = []
    current_node = tp.__class__
    while current_node != object:
        result.append(current_node)
        current_node = current_node.__base__
    return result


def __types_lca(lhs_type: Type, rhs_type: Type):
    lhs_path, rhs_path = __unroll_type_tree(lhs_type), __unroll_type_tree(rhs_type)
    idx = 0
    while idx < min(len(lhs_path), len(rhs_path)) and lhs_path[-idx] == rhs_path[-idx]:
        idx += 1
    return lhs_path[1 - idx]


def __common_type(lhs_type: Type, rhs_type: Type) -> typing.Union[Type | None]:
    if lhs_type == rhs_type:
        return lhs_type
    lca_type = __types_lca(lhs_type, rhs_type)
    if lca_type == NumericT or lca_type == IntegerT or lca_type == FloatT:
        return lhs_type.priority if lhs_type.priority > rhs_type.priority else rhs_type.priority
    elif lca_type == PointerT:
        ptr_type = __common_type(lhs_type.type, rhs_type.type)
        if ptr_type is None:
            return None
        return PointerT(ptr_type)
    elif lca_type == ProcedureT:
        return_type = __common_type(lhs_type.retT, rhs_type.retT)
        if return_type is None or len(lhs_type.argsT) != len(rhs_type.argsT):
            return None
        args_type = [__common_type(lhs_arg_type, rhs_arg_type) for lhs_arg_type, rhs_arg_type in zip(lhs_type.argsT, rhs_type.argsT)]
        if any([arg_type is None for arg_type in args_type]):
            return None
        return ProcedureT(return_type, args_type)
    elif lca_type == ArrayT:
        arr_type = __common_type(lhs_type.type, rhs_type.type)
        if arr_type is None or lhs_type.size != rhs_type.size:
            return None
        return ArrayT(arr_type, lhs_type.size)
    return None

def common_type(*args, types: typing.List[Type]=None):
    result = None
    if len(args) > 0:
        result = args[0]
        if len(args) > 1:
            result = __common_type(args[0], args[1])
            for idx in range(2, len(args)):
                result = __common_type(result, args[idx])
    if types is not None and len(types) > 0:
        if result is not None:
            types = [result] + types
        result = types[0]
        if len(types) > 1:
            result = __common_type(types[0], types[1])
            for idx in range(2, len(types)):
                result = __common_type(result, args[idx])
    return result