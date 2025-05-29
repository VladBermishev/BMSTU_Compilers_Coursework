import pathlib
import os
os.environ['LLVMLITE_ENABLE_OPAQUE_POINTERS'] = '1'
import llvmlite
import llvmlite.binding
llvmlite.opaque_pointers_enabled = True
import llvmlite.ir.values as llvm_values
import llvmlite.ir.instructions as llvm_instructions
import llvmlite.ir.types as llvm_types
import llvmlite.ir.module as llvm_module
import llvmlite.ir.builder as llvm_builder

#HACKS
llvm_types.PointerType.as_pointer = lambda self, addrspace=0: llvm_types.PointerType(addrspace=addrspace)
llvm_types.PointerType.intrinsic_name = 'p0'
llvm_types.PointerType.__eq__ = lambda self, other: isinstance(other, llvm_types.PointerType)

import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
import src.hir.values as hir_values
import src.hir.module as hir_module
from src.codegen.hir_to_llvm_mappings import HirToLLVMTypesMapping


class LLVMTransform:
    zero = llvm_values.Constant(llvm_types.IntType(32), 0)
    zerou1 = llvm_values.Constant(llvm_types.IntType(1), 0)
    one = llvm_values.Constant(llvm_types.IntType(32), 1)

    @staticmethod
    def transform(node, _parent=None, _st=None):
        match type(node):
            case t if t is hir_module.Module:
                return LLVMTransformModule.transform(node)
            case t if t is hir_values.GlobalVariable:
                return LLVMTransformGlobalVariable.transform(node, _parent, _st)
            case t if t is hir_values.Function:
                return LLVMTransformFunction.transform(node, _parent, _st)
            case t if t is hir_values.ConstantValue:
                value = node.value
                if isinstance(value, list):
                    value = [LLVMTransform.transform(elem) for elem in value]
                elif isinstance(node.type, hir_types.PointerType):
                    value = None
                elif isinstance(value, str):
                    value = [ llvm_values.Constant(llvm_types.IntType(32), ord(c)) for c in value]
                return llvm_values.Constant(HirToLLVMTypesMapping.get(node.type), value)
        return None

    @staticmethod
    def build(builder: llvm_builder.IRBuilder, instr: hir_instructions.Instruction, _st=None):
        def _add_symbol(llvm_instruction):
            if instr.name != hir_values.NamedValue.empty_name:
                _st[instr.get_reference()] = llvm_instruction
        def _get_operand(operand):
            if isinstance(operand, hir_values.ConstantValue):
                return LLVMTransform.transform(operand)
            else:
                return _st[operand.get_reference()]

        match type(instr):
            case t if t is hir_instructions.Instruction:
                llvm_operands = [_get_operand(operand) for operand in instr.operands]
                llvm_instr = llvm_instructions.Instruction(
                    builder.block, HirToLLVMTypesMapping.get(instr.type),
                    instr.opname, llvm_operands, instr.name
                )
                builder._insert(llvm_instr)
                _add_symbol(llvm_instr)
            case t if t is hir_instructions.CallInstruction:
                func = _st[instr.operands[0].get_reference()]
                args = [_get_operand(arg) for arg in instr.operands[1:]]
                _add_symbol(builder.call(func, args, instr.name))
            case t if t is hir_instructions.ReturnInstruction:
                if len(instr.operands) > 0:
                    builder.ret(_get_operand(instr.operands[0]))
                else:
                    builder.ret_void()
            case t if t is hir_instructions.BranchInstruction:
                block = _st[instr.operands[0].name]
                builder.branch(block)
            case t if t is hir_instructions.ConditionalBranchInstruction:
                cond = _get_operand(instr.operands[0])
                true_block, false_block = _st[instr.operands[1].name], _st[instr.operands[2].name]
                builder.cbranch(cond, true_block, false_block)
            case t if t is hir_instructions.SelectInstruction:
                cond = _get_operand(instr.operands[0])
                true_val, false_val = _st[instr.operands[1].name], _st[instr.operands[2].name]
                _add_symbol(builder.select(cond, true_val, false_val, instr.name))
            case t if t is hir_instructions.IntCompareInstruction:
                lhs, rhs = _get_operand(instr.operands[0]), _get_operand(instr.operands[1])
                cmp_instr = llvm_instructions.ICMPInstr(builder.block, instr.op, lhs, rhs, instr.name)
                _add_symbol(cmp_instr)
                builder._insert(cmp_instr)
            case t if t is hir_instructions.FloatCompareInstruction:
                lhs, rhs = _get_operand(instr.operands[0]), _get_operand(instr.operands[1])
                cmp_instr = llvm_instructions.FCMPInstr(builder.block, instr.op, lhs, rhs, instr.name)
                _add_symbol(cmp_instr)
                builder._insert(cmp_instr)
            case t if t is hir_instructions.CastInstruction:
                value = _get_operand(instr.operands[0])
                cast_instr = llvm_instructions.CastInstr(builder.block, instr.opname, value, HirToLLVMTypesMapping.get(instr.type), instr.name)
                _add_symbol(cast_instr)
                builder._insert(cast_instr)
            case t if t is hir_instructions.LoadInstruction:
                load_instr = builder.load(_get_operand(instr.operands[0]), instr.name, typ=HirToLLVMTypesMapping.get(instr.type))
                _add_symbol(load_instr)
            case t if t is hir_instructions.StoreInstruction:
                builder.store(_get_operand(instr.operands[0]), _get_operand(instr.operands[1]))
            case t if t is hir_instructions.CopyInstruction:
                if "llvm.memcpy" not in _st:
                    fn = builder.module.declare_intrinsic("llvm.memcpy", [llvm_types.PointerType(), llvm_types.PointerType(), llvm_types.IntType(32)])
                    _st["llvm.memcpy"] = fn
                builder.call(_st["llvm.memcpy"], [_get_operand(operand) for operand in instr.operands] + [LLVMTransform.zerou1])
            case t if t is hir_instructions.AllocateInstruction:
                size = LLVMTransform.transform(instr.operands[0]) if len(instr.operands) > 0 else None
                _add_symbol(builder.alloca(HirToLLVMTypesMapping.get(instr.allocated_type), size, instr.name))
            case t if t is hir_instructions.GEPInstruction:
                ptr = _get_operand(instr.operands[0])
                indices = [_get_operand(operand) for operand in instr.operands[1:]]
                gep_instr = builder.gep(ptr, indices, True, name=instr.name, source_etype=HirToLLVMTypesMapping.get(instr.source_etype))
                gep_instr.type = llvm_types.PointerType()
                _add_symbol(gep_instr)
                #_add_symbol(builder.gep(ptr, indices, name=instr.name))
            case t if t is hir_instructions.PhiInstruction:
                phi_instr = builder.phi(HirToLLVMTypesMapping.get(instr.type), instr.name)
                for (inc_value, inc_block) in instr.incomings:
                    phi_instr.add_incoming(_get_operand(inc_value), _st[inc_block.name])
                _add_symbol(phi_instr)

class LLVMTransformModule:
    @staticmethod
    def transform(node: hir_module.Module):
        module = llvm_module.Module(name=node.name)
        module.triple = llvmlite.binding.get_default_triple()
        hir_symbol_table = {}
        for global_val in node.globals:
            LLVMTransform.transform(global_val, module, hir_symbol_table)
        if len(node.constructors) > 0:
            ctor_struct_type = llvm_types.LiteralStructType([llvm_types.IntType(32), llvm_types.PointerType(), llvm_types.PointerType()])
            llvm_global_ctor = llvm_values.GlobalVariable(module, llvm_types.ArrayType(ctor_struct_type, 1), "llvm.global_ctors")
            llvm_global_ctor.linkage = "appending"
            ctors = [LLVMTransform.transform(global_ctor, module, hir_symbol_table) for global_ctor in node.constructors]
            global_ctor = llvm_values.Function(module,
                                               llvm_types.FunctionType(llvm_types.VoidType(), []),
                                               name=f"_GLOBAL__sub_I_{pathlib.Path(module.name).name}"
                                               )
            global_ctor.section = ".text.startup"
            global_ctor.linkage = "internal"
            llvm_global_ctor.initializer = (
                llvm_values.Constant(llvm_global_ctor.value_type,
                                     [llvm_values.Constant(ctor_struct_type, [
                                         llvm_values.Constant(llvm_types.IntType(32), 65535),
                                         global_ctor,
                                         llvm_values.Constant(llvm_types.PointerType(), "null")
                                     ])]
                                     )
            )
            builder = llvm_builder.IRBuilder(global_ctor.append_basic_block("entry"))
            for ctor in ctors:
                ctor.section = ".text.startup"
                ctor.linkage = "internal"
                builder.call(ctor, [])
            builder.ret_void()
        return module

class LLVMTransformGlobalVariable:
    @staticmethod
    def transform(node: hir_values.GlobalVariable, _parent=None, st=None):
        result = llvm_values.GlobalVariable(_parent, HirToLLVMTypesMapping.get(node.value_type), node.name)
        if isinstance(node.init_value, hir_values.ConstantValue):
            result.initializer = LLVMTransform.transform(node.init_value, _parent, st)
        else:
            result.initializer = st[node.init_value.get_reference()]
        result.global_constant = node.global_constant
        st[node.get_reference()] = result
        return result

class LLVMTransformFunction:
    @staticmethod
    def transform(node: hir_values.Function, _parent=None, st=None):
        func = llvm_values.Function(_parent, HirToLLVMTypesMapping.get(node.ftype), node.name)
        for hir_arg, llvm_arg in zip(node.args, func.args):
            llvm_arg.name = hir_arg.name
            st[hir_arg.get_reference()] = llvm_arg
        st[node.get_reference()] = func
        for hir_block in node.blocks:
            st[hir_block.name] = func.append_basic_block(hir_block.name)
        for hir_block in node.blocks:
            builder = llvm_builder.IRBuilder(st[hir_block.name])
            for instr in hir_block.instructions:
                LLVMTransform.build(builder, instr, st)
        return func

