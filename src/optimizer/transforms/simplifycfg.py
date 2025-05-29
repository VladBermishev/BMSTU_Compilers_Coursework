from collections import defaultdict

import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions

class SimplifyCFGTransform:

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        """Transform each function in the module."""
        for constructor in module.constructors:
            SimplifyCFGFunctionTransform.transform(constructor)
        for func in module.globals:
            SimplifyCFGFunctionTransform.transform(func)
        return module

class SimplifyCFGFunctionTransform:
    MAX_ITER = 10

    class CFGNode:
        def __init__(self, parents=None, children=None):
            self.parents = parents or []
            self.children = children or []

    def __init__(self, function: hir_values.Function):
        self.cfg_nodes = SimplifyCFGFunctionTransform.__build_cfg_nodes(function)

    @staticmethod
    def transform(function: hir_values.Function):
        transformer = SimplifyCFGFunctionTransform(function)
        for iteration in range(SimplifyCFGFunctionTransform.MAX_ITER):
            modified = False
            modified |= transformer.__remove_unreachable_blocks(function)
            modified |= transformer.__merge_blocks(function)
            if not modified:
                break

    def __remove_unreachable_blocks(self, function: hir_values.Function):
        stack = [function.blocks[0]]
        reachable_blocks = set()
        while len(stack) > 0:
            block = stack.pop()
            reachable_blocks.add(block)
            if isinstance(block.terminator, hir_instructions.BranchInstruction):
                stack.append(block.terminator.operands[0])
            elif isinstance(block.terminator, hir_instructions.ConditionalBranchInstruction):
                stack.append(block.terminator.operands[1])
                stack.append(block.terminator.operands[2])
        result = len(reachable_blocks) != len(function.blocks)
        function.blocks = [block for block in function.blocks if block in reachable_blocks]
        return result

    @staticmethod
    def __build_cfg_nodes(function: hir_values.Function):
        result = defaultdict(SimplifyCFGFunctionTransform.CFGNode)
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

    def __merge_blocks(self, function: hir_values.Function):
        self.cfg_nodes = SimplifyCFGFunctionTransform.__build_cfg_nodes(function)
        for block in function.blocks:
            block_succ_cnt = len(self.cfg_nodes[block].children)
            succ_pred_cnt = len(self.cfg_nodes[block.terminator.operands[0]].parents)
            if isinstance(block.terminator, hir_instructions.BranchInstruction) and block_succ_cnt == 1 and succ_pred_cnt == 1:
                succ = block.terminator.operands[0]
                block.terminator = succ.terminator
                block.instructions = block.instructions[:-1] + succ.instructions
                function.blocks.remove(succ)
                self.cfg_nodes = SimplifyCFGFunctionTransform.__build_cfg_nodes(function)
                for child in self.cfg_nodes[block].children:
                    for instruction in child.instructions:
                        if isinstance(instruction, hir_instructions.PhiInstruction):
                            instruction.incomings = [(val, block if blk is succ else blk) for (val, blk) in instruction.incomings]
                return True
        return False

    def __simplify_branches(self, function: hir_values.Function):
        result = False
        for block in list(function.blocks):
            if isinstance(block.terminator, hir_instructions.BranchInstruction):
                if (new_target := self.__skip_empty_block(function, block)) != block.terminator.operands[0]:
                    block.terminator.operands[0] = new_target
                    block.instructions[-1].operands[0] = new_target
                    result = True
            elif isinstance(block.terminator, hir_instructions.ConditionalBranchInstruction):
                true_dest = self.__skip_empty_block(function, block.terminator.operands[1])
                false_dest = self.__skip_empty_block(function, block.terminator.operands[2])
                # Constant condition
                if isinstance(block.terminator.operands[0], hir_values.ConstantValue):
                    target = block.terminator.operands[1] if block.terminator.operands[0].value else block.terminator.operands[2]
                    block.terminator = hir_instructions.BranchInstruction(block, target)
                    block.instructions[-1] = block.terminator
                    result = True

                # Both destinations are the same
                elif block.terminator.operands[1] == block.terminator.operands[2]:
                    block.terminator = hir_instructions.BranchInstruction(block, block.terminator.operands[1])
                    block.instructions[-1] = block.terminator
                    result = True
                elif true_dest != block.terminator.operands[1] or false_dest != block.terminator.operands[2]:
                    block.terminator.operands[1] = true_dest
                    block.terminator.operands[2] = false_dest
                    result = True
                else:
                    preds = self.cfg_nodes[block].parents
                    is_conditional = isinstance(preds[0].terminator, hir_instructions.ConditionalBranchInstruction)
                    if len(preds) == 1 and is_conditional and:


        return result

    def __skip_empty_block(self, function: hir_values.Function, entry_block: hir_values.Block):
        new_target = entry_block.terminator.operands[0]
        while len(new_target.instructions) == 1 and isinstance(new_target.terminator, hir_instructions.BranchInstruction):
            new_target = new_target.terminator.operands[0]
        return new_target



