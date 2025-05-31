from collections import defaultdict
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions

class CFGNode:
    def __init__(self, parents=None, children=None):
        self.parents = parents or []
        self.children = children or []

    @staticmethod
    def build_nodes(function: hir_values.Function):
        result = defaultdict(CFGNode)
        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, hir_instructions.BranchInstruction):
                    result[block].children.append(inst.operands[0])
                    result[inst.operands[0]].parents.append(block)
                elif isinstance(inst, hir_instructions.ConditionalBranchInstruction):
                    result[block].children.append(inst.operands[1])
                    result[inst.operands[1]].parents.append(block)
                    result[block].children.append(inst.operands[2])
                    result[inst.operands[2]].parents.append(block)
        return result

    @staticmethod
    def preds(function: hir_values.Function, block: hir_values.Block):
        result = []
        cfg_node = CFGNode.build_nodes(function)
        st = [block]
        while len(st) > 0:
            curr, st = st[0], st[1:]
            for parent in cfg_node[curr].parents:
                if parent not in result:
                    result.append(parent)
                    st.append(parent)
        return result
