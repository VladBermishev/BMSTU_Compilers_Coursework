from llvmlite import ir, binding


class OpaquePointerType(ir.PointerType):
    """
    The type of all pointer values.
    """
    is_pointer = True
    null = 'null'

    def __init__(self, pointee=ir.VoidType(), addrspace=0):
        self.is_opaque = isinstance(pointee, ir.VoidType)
        self.pointee = pointee
        self.addrspace = addrspace

    def _to_string(self):
        if self.is_opaque:
            return "ptr"
        elif self.addrspace != 0:
            return "{0} addrspace({1})*".format(self.pointee, self.addrspace)
        else:
            return "{0}*".format(self.pointee)

    def __str__(self):
        return "ptr"

    def __eq__(self, other):
        if isinstance(other, ir.PointerType):
            return (self.pointee, self.addrspace) == (other.pointee, other.addrspace)
        else:
            return False

    def __hash__(self):
        return hash(ir.PointerType)

    def gep(self, i):
        """
        Resolve the type of the i-th element (for getelementptr lookups).
        """
        if not isinstance(i.type, ir.IntType):
            raise TypeError(i.type)
        return self.pointee

    @property
    def intrinsic_name(self):
        return 'p%d%s' % (self.addrspace, self.pointee.intrinsic_name)


class GlobalConstructor(ir.GlobalValue):
    """
        A global variable.
        """

    def __init__(self, module, constructor_name=None, addrspace=0):
        self.value_type = ir.ArrayType(ir.LiteralStructType([ir.IntType(32), OpaquePointerType(), OpaquePointerType()]), 1)
        super(GlobalConstructor, self).__init__(module, self.value_type.as_pointer(addrspace), name="llvm.global_ctors")
        self.initializer = None
        if constructor_name:
            self.set_constructor_function_name(constructor_name)
        self.unnamed_addr = False
        self.addrspace = addrspace
        self.align = None
        self.parent.add_global(self)

    def descr(self, buf):
        kind = "appending global"
        buf.append("{kind} {type}".format(kind=kind, type=self.value_type))
        if self.initializer.type != self.value_type:
            raise TypeError("got initializer of type %s "
                            "for global value type %s"
                            % (self.initializer.type, self.value_type))
        buf.append(" " + self.initializer.get_reference())
        buf.append("\n")

    def set_constructor_function_name(self, name: str):
        const_val = ir.Constant(self.value_type, [[ir.Constant(ir.IntType(32), 65535),
                                 ir.Constant(OpaquePointerType(), f"@{name}"),
                                 ir.Constant(OpaquePointerType(), "null")]])
        self.initializer = const_val


def label_suffix(label, suffix):
    """Returns (label + suffix) or a truncated version if it's too long.
    Parameters
    ----------
    label : str
        Label name
    suffix : str
        Label suffix
    """
    if len(label) > 50:
        nhead = 25
        return ''.join([label[:nhead], '..', suffix])
    else:
        return label + suffix


class GEPOpaqueInstr(ir.Instruction):
    def __init__(self, parent, ptr, indices, inbounds, name):
        typ = OpaquePointerType()
        super(GEPOpaqueInstr, self).__init__(parent, typ, "getelementptr",
                                       [ptr] + list(indices), name=name)
        self.pointer = ptr
        self.indices = indices
        self.inbounds = inbounds

    def descr(self, buf):
        indices = ['{0} {1}'.format(i.type, i.get_reference())
                   for i in self.indices]
        op = "getelementptr inbounds" if self.inbounds else "getelementptr"
        buf.append("{0} {1}, {2} {3}, {4} {5}\n".format(
                   op,
                   self.pointer.type.pointee,
                   self.pointer.type,
                   self.pointer.get_reference(),
                   ', '.join(indices),
                   self._stringify_metadata(leading_comma=True),
                   ))


def gep_opaque(self, ptr, indices, inbounds=False, name=''):
    instr = GEPOpaqueInstr(self.block, ptr, indices, inbounds=inbounds, name=name)
    self._insert(instr)
    return instr


#ir.IRBuilder.gep_opaque = gep_opaque
