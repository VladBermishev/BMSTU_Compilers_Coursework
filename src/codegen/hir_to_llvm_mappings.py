import llvmlite
llvmlite.opaque_pointers_enabled = True
import src.hir.types as hir_types
import llvmlite.ir.values as llvm_values
import llvmlite.ir.types as llvm_types
import llvmlite.ir.module as llvm_module
import llvmlite.ir.builder as llvm_builder

class HirToLLVMTypesMapping:
    _TP_MAP = {
        hir_types.Type: llvm_types.Type,
        hir_types.VoidType: llvm_types.VoidType,
        hir_types.BoolType: lambda: llvm_types.IntType(1),
        hir_types.IntType: lambda: llvm_types.IntType(32),
        hir_types.LongType: lambda: llvm_types.IntType(64),
        hir_types.FloatType: llvm_types.FloatType,
        hir_types.DoubleType: llvm_types.DoubleType,
        hir_types.PointerType: llvm_types.PointerType,
        hir_types.ArrayType: llvm_types.ArrayType,
        hir_types.FunctionType: llvm_types.FunctionType,
        hir_types.StructType: llvm_types.LiteralStructType,
    }
    @staticmethod
    def get(hir_type: hir_types.Type):
        match type(hir_type):
            case t if t is hir_types.ArrayType:
                return llvm_types.ArrayType(HirToLLVMTypesMapping.get(hir_type.element), hir_type.count)
            case t if t is hir_types.FunctionType:
                arguments = map(HirToLLVMTypesMapping.get, hir_type.args)
                return llvm_types.FunctionType(HirToLLVMTypesMapping.get(hir_type.return_type), arguments)
            case t if t is hir_types.StructType:
                return llvm_types.LiteralStructType([HirToLLVMTypesMapping.get(struct_type) for struct_type in hir_type.elements_types ])
        return HirToLLVMTypesMapping._TP_MAP[type(hir_type)]()