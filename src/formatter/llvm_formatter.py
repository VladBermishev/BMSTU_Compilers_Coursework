import sys
import struct
import os
os.environ['LLVMLITE_ENABLE_OPAQUE_POINTERS'] = '1'
import llvmlite
llvmlite.opaque_pointers_enabled = True
import llvmlite.binding
import llvmlite.ir.values as llvm_values
import llvmlite.ir.instructions as llvm_instructions
import llvmlite.ir.types as llvm_types
import llvmlite.ir.module as llvm_module
import llvmlite.ir.builder as llvm_builder

class LLVMFormatter:
    @staticmethod
    def print(module: llvm_module.Module, file=sys.stdout):
        def __descr(self, buf):
            self.descr_prototype(buf)
            buf[-1] = buf[-1][:-1]
            if self.blocks:
                buf.append("{\n")
                self.descr_body(buf)
                buf.append("}\n")

        def __descr_body(self, buf):
            """
            Describe of the body of the function.
            """
            self.blocks[0].descr(buf)
            for blk in self.blocks[1:]:
                buf.append("\n")
                blk.descr(buf)

        def __get_reference(self):
            name = self.name
            return '{0}{1}'.format(self.name_prefix, name)

        def __format_float_as_hex(value, packfmt, unpackfmt, numdigits):
            raw = struct.pack(packfmt, float(value))
            intrep = struct.unpack(unpackfmt, raw)[0]
            out = '{{0:#{0}x}}'.format(numdigits).format(intrep)
            return out.strip()

        llvm_values.NamedValue._get_reference = __get_reference
        llvm_types._format_float_as_hex = __format_float_as_hex
        llvm_values.Function.descr = __descr
        llvm_values.Function.descr_body = __descr_body
        file.write(str(module))