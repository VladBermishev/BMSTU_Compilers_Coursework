import llvmlite
llvmlite.opaque_pointers_enabled = True
import llvmlite.ir.values as llvm_values
import llvmlite.ir.types as llvm_types
import llvmlite.ir.module as llvm_module
import llvmlite.ir.builder as llvm_builder
import src.hir.types as hir_types
import src.hir.values as hir_values
import src.hir.module as hir_module

class LLVMTransform:
    zero = llvm_values.Constant(llvm_types.IntType(32), 0)
    one = llvm_values.Constant(llvm_types.IntType(32), 1)

    @staticmethod
    def transform(node, _parent=None, _st=None):
        match type(node):
            case t if t is hir_module.Module:
                return LLVMTransformModule.transform(node, st=_st)
            case t if t is hir_values.GlobalVariable:
                return LLVMTransformGlobalVariable.transform(node)
            case t if t is hir_values.Function:
                return LLVMTransformFunction.transform(node)
        return None

class LLVMTransformModule:
    @staticmethod
    def transform(node: hir_module.Module, _parent=None, st=None):
        module = llvm_module.Module(name=node.name)
        ctor_struct_type = llvm_types.LiteralStructType([llvm_types.IntType(32), llvm_types.PointerType(), llvm_types.PointerType()])
        llvm_global_ctor = llvm_values.GlobalVariable(module, llvm_types.ArrayType(ctor_struct_type, 1), "llvm.global_ctors")
        #ir.ArrayType(ir.LiteralStructType([ir.IntType(32), OpaquePointerType(), OpaquePointerType()]), 1)
        global_ctor = llvm_values.Function(module, llvm_types.FunctionType(llvm_types.VoidType(), []), name="main")
        llvm_values.Constant(llvm_global_ctor.value_type,
                             llvm_values.Constant(ctor_struct_type, [
                                 [llvm_values.Constant(llvm_types.IntType(32), 65535),
                                  global_ctor,
                                  llvm_values.Constant(llvm_types.PointerType(), "null")]
                             ]))
        ctors = [LLVMTransformGlobalVariable.transform(global_ctor, module, st) for global_ctor in node.constructors]
        for ctor in ctors:
            module.add_global(LLVMTransformGlobalVariable.transform(ctor, module, st))
        for global_val in node.globals:
            module.add_global(LLVMTransformGlobalVariable.transform(global_val, module, st))

class LLVMTransformGlobalVariable:
    @staticmethod
    def transform(node: hir_values.GlobalVariable, _parent=None, st=None):
        pass

class LLVMTransformFunction:
    @staticmethod
    def transform(node: hir_values.Function, _parent=None, st=None):
        pass