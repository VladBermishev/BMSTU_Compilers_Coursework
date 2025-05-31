import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.hir.instructions import PhiInstruction
from src.optimizer.analyzers.cfgnode import CFGNode
from src.optimizer.analyzers.domtree import DomTree
from src.optimizer.analyzers.ssa import SSA

class DCETransform:

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        for global_value in module.globals:
            if isinstance(global_value, hir_values.Function) and len(global_value.blocks) > 0:
                DCEFunctionTransform.transform(global_value)
        return module

class DCEFunctionTransform:
    @staticmethod
    def transform(function: hir_values.Function):
        ssa_cnt = {}
        for ssa_node in SSA.ssa_nodes(function):
            ssa_cnt[ssa_node] = 0
        for ssa_value, cnt in ssa_cnt.items():
            for block in function.blocks:
                for instr in block.instructions:
                    if instr != ssa_value:
                        if isinstance(instr, PhiInstruction):
                            ssa_cnt[ssa_value] += 1 if ssa_value in [inc[0] for inc in instr.incomings] else 0
                        else:
                            ssa_cnt[ssa_value] += 1 if ssa_value in instr.operands else 0
        while DCEFunctionTransform.__ssa_cnt_with_value(ssa_cnt, 0) > 0:
            for instr, cnt in ssa_cnt.items():
                if isinstance(instr, hir_values.Argument):
                    continue
                if cnt == 0:
                    if isinstance(instr, PhiInstruction):
                        for incoming in instr.incomings:
                            if incoming[0] in ssa_cnt:
                                ssa_cnt[incoming[0]] -= 1
                    else:
                        for operand in instr.operands:
                            if operand in ssa_cnt:
                                ssa_cnt[operand] -= 1
                    instr.parent.instructions.remove(instr)
                    ssa_cnt.pop(instr)
                    break

    @staticmethod
    def __ssa_cnt_with_value(ssa_cnt, value):
        result = 0
        for ssa_value, cnt in ssa_cnt.items():
            if cnt == value and not isinstance(ssa_value, hir_values.Argument):
                result += 1
        return result