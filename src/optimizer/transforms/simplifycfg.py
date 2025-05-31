from collections import defaultdict
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.optimizer.analyzers.cfgnode import CFGNode


class SimplifyCFGTransform:

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        """Transform each function in the module."""
        for constructor in module.constructors:
            SimplifyCFGFunctionTransform.transform(constructor)
        for global_value in module.globals:
            if isinstance(global_value, hir_values.Function) and len(global_value.blocks) > 0:
                SimplifyCFGFunctionTransform.transform(global_value)
        return module

class SimplifyCFGFunctionTransform:
    MAX_ITER = 10

    def __init__(self, function: hir_values.Function):
        self.cfg_nodes = CFGNode.build_nodes(function)
        self.block_phi_replacements = defaultdict(set)
        for block in function.blocks:
            self.block_phi_replacements[block] = set()

    @staticmethod
    def transform(function: hir_values.Function):
        transformer = SimplifyCFGFunctionTransform(function)
        for iteration in range(SimplifyCFGFunctionTransform.MAX_ITER):
            modified = False
            modified |= transformer.__remove_unreachable_blocks(function)
            modified |= transformer.__merge_blocks(function)
            modified |= transformer.__simplify_branches(function)
            transformer.__fix_instr_parent(function)
            if not modified:
                break

    def __remove_unreachable_blocks(self, function: hir_values.Function):
        stack = [function.blocks[0]]
        reachable_blocks = set()
        while len(stack) > 0:
            block = stack.pop()
            reachable_blocks.add(block)
            if isinstance(block.terminator, hir_instructions.BranchInstruction):
                if block.terminator.operands[0] not in reachable_blocks:
                    stack.append(block.terminator.operands[0])
            elif isinstance(block.terminator, hir_instructions.ConditionalBranchInstruction):
                if block.terminator.operands[1] not in reachable_blocks:
                    stack.append(block.terminator.operands[1])
                if block.terminator.operands[2] not in reachable_blocks:
                    stack.append(block.terminator.operands[2])
        result = len(reachable_blocks) != len(function.blocks)
        function.blocks = [block for block in function.blocks if block in reachable_blocks]
        for block in function.blocks:
            for instr in block.instructions:
                if isinstance(instr, hir_instructions.PhiInstruction):
                    incomings = []
                    for val, block in instr.incomings:
                        if block not in reachable_blocks and block in self.block_phi_replacements:
                            for new_block in self.block_phi_replacements[block]:
                                incomings.append((val, new_block))
                        else:
                            incomings.append((val, block))
                    instr.incomings = incomings
        #self.block_phi_replacements = {k: v for k, v in self.block_phi_replacements.items() if k in reachable_blocks}
        self.cfg_nodes = CFGNode.build_nodes(function)
        return result

    def __merge_blocks(self, function: hir_values.Function):
        self.cfg_nodes = CFGNode.build_nodes(function)
        for block in function.blocks:
            block_succ_cnt = len(self.cfg_nodes[block].children)
            if block_succ_cnt == 1:
                succ_pred_cnt = len(self.cfg_nodes[block.terminator.operands[0]].parents)
                if isinstance(block.terminator, hir_instructions.BranchInstruction) and succ_pred_cnt == 1:
                    succ = block.terminator.operands[0]
                    block.terminator = succ.terminator
                    block.instructions = block.instructions[:-1] + succ.instructions
                    function.blocks.remove(succ)
                    self.cfg_nodes = CFGNode.build_nodes(function)
                    for child in self.cfg_nodes[block].children:
                        for instruction in child.instructions:
                            if isinstance(instruction, hir_instructions.PhiInstruction):
                                instruction.incomings = [(val, block if blk is succ else blk) for (val, blk) in instruction.incomings]
                    return True
            elif block_succ_cnt == 2:
                true_br, false_br = block.terminator.operands[1], block.terminator.operands[2]
                succ_to_merge = None
                if len(self.cfg_nodes[true_br].parents) == 1:
                    succ_to_merge = true_br
                elif len(self.cfg_nodes[false_br].parents) == 1:
                    succ_to_merge = false_br
                if succ_to_merge is None:
                    return False
                can_merge = True
                for instr in succ_to_merge.instructions:
                    if isinstance(instr, (hir_instructions.PhiInstruction, hir_instructions.StoreInstruction, hir_instructions.CallInstruction)):
                        can_merge = False
                        break
                if can_merge and isinstance(succ_to_merge.terminator, hir_instructions.ConditionalBranchInstruction):
                    succ_to_test = false_br if succ_to_merge is true_br else true_br

                    # Need to insert select
                    if succ_to_test in succ_to_merge.terminator.operands[1:]:
                        succ_true, succ_false = succ_to_merge.terminator.operands[1], succ_to_merge.terminator.operands[2]
                        if succ_to_merge is true_br:
                            new_true, new_false = succ_to_test, succ_true if succ_to_test is succ_false else succ_false
                            new_lhs_cond = hir_values.ConstantValue(hir_types.BoolType(),0)
                            new_rhs_cond = succ_to_merge.terminator.operands[0]
                        else:
                            new_true, new_false = succ_true if succ_to_test is succ_false else succ_false, succ_to_test
                            new_lhs_cond = succ_to_merge.terminator.operands[0]
                            new_rhs_cond = hir_values.ConstantValue(hir_types.BoolType(), 1)
                        select_instr = hir_instructions.SelectInstruction(block,
                                                                          block.terminator.operands[0],
                                                                          new_lhs_cond,
                                                                          new_rhs_cond)
                        branch_instr = hir_instructions.ConditionalBranchInstruction(block,
                                                                                     select_instr,
                                                                                     new_true,
                                                                                     new_false)
                        block.instructions = block.instructions[:-1] + succ_to_merge.instructions[:-1] + [select_instr, branch_instr]
                        block.terminator = branch_instr
                        return True


        return False

    def __simplify_branches(self, function: hir_values.Function):
        result = False
        for block in function.blocks:
            if isinstance(block.terminator, hir_instructions.BranchInstruction):
                if (new_target := self.__skip_empty_block(function, block.terminator.operands[0])) != block.terminator.operands[0]:
                    self.__traverse_empty_block(function, block, block.terminator.operands[0])
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

                # Fallthrough empty blocks
                elif true_dest != block.terminator.operands[1] or false_dest != block.terminator.operands[2]:
                    self.__traverse_empty_block(function, block, block.terminator.operands[1])
                    self.__traverse_empty_block(function, block, block.terminator.operands[2])
                    block.terminator.operands[1] = true_dest
                    block.terminator.operands[2] = false_dest
                    result = True

                # If pred condition is identical to block cond
                else:
                    preds = self.cfg_nodes[block].parents
                    if len(preds) == 1:
                        is_conditional = isinstance(preds[0].terminator, hir_instructions.ConditionalBranchInstruction)
                        block_cond = block.terminator.operands[0]
                        pred_cond = preds[0].terminator.operands[0]
                        if is_conditional and pred_cond.is_related(block_cond):
                            if pred_cond.is_identical(block_cond):
                                new_target = block.terminator.operands[1 if block is preds[0].terminator.operands[1] else 2]
                                block.terminator = hir_instructions.BranchInstruction(block, new_target)
                                block.instructions[-1] = block.terminator
                                self.block_phi_replacements[block] = preds[0]
                                result = True
                            elif pred_cond.is_negated(block_cond):
                                new_target = block.terminator.operands[2 if block is preds[0].terminator.operands[1] else 1]
                                block.terminator = hir_instructions.BranchInstruction(block, new_target)
                                block.instructions[-1] = block.terminator
                                self.block_phi_replacements[block] = preds[0]
                                result = True
        return result

    def __skip_empty_block(self, function: hir_values.Function, entry_block: hir_values.Block):
        if len(entry_block.instructions) == 1 and isinstance(entry_block.terminator, hir_instructions.BranchInstruction):
            new_target = entry_block.terminator.operands[0]
            while len(new_target.instructions) == 1 and isinstance(new_target.terminator, hir_instructions.BranchInstruction):
                new_target = new_target.terminator.operands[0]
            return new_target
        return entry_block

    def __traverse_empty_block(self, function: hir_values.Function, entry_block: hir_values.Block, succ_block):
        self.block_phi_replacements[succ_block].add(entry_block)
        if len(succ_block.instructions) == 1 and isinstance(succ_block.terminator, hir_instructions.BranchInstruction):
            new_target = succ_block.terminator.operands[0]
            while len(new_target.instructions) == 1 and isinstance(new_target.terminator, hir_instructions.BranchInstruction):
                new_target = new_target.terminator.operands[0]
                self.block_phi_replacements[new_target].add(entry_block)

    def __fix_instr_parent(self, function: hir_values.Function):
        for block in function.blocks:
            for instruction in block.instructions:
                instruction.parent = block
            block.terminator.parent = block

