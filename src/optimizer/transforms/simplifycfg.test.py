from src.codegen.hir.hir_module import Module
from src.codegen.hir.hir_values import BasicBlock, Function, Value, Instruction
from src.codegen.hir.hir_instructions import (
    BranchInst, ReturnInst, PhiInst, BinaryInst,
    CompareInst, ConstantInt, Constant, LoadInst, StoreInst, CallInst
)
from typing import List, Set, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SimplifyCFGTransform:
    def __init__(self):
        self.modified = False
        self.max_iterations = 4  # LLVM uses 4 as default

    @staticmethod
    def transform(module: Module) -> Module:
        transformer = SimplifyCFGTransform()
        return transformer._transform_module(module)

    def _transform_module(self, module: Module) -> Module:
        for constructor in module.constructors:
            self._transform_function(constructor)
        return module

    def _transform_function(self, function: Function) -> None:
        """Apply CFG simplifications iteratively."""
        iteration = 0
        while iteration < self.max_iterations:
            self.modified = False

            # Apply transformations in specific order
            self._eliminate_unreachable_blocks(function)
            self._merge_blocks(function)
            self._eliminate_dead_switches(function)
            self._simplify_jumps(function)
            self._hoist_common_code(function)
            self._eliminate_empty_blocks(function)
            self._combine_duplicate_blocks(function)
            self._simplify_terminator_instructions(function)

            if not self.modified:
                break
            iteration += 1

    def _eliminate_unreachable_blocks(self, function: Function) -> None:
        """Remove blocks that cannot be reached from entry."""
        reachable = self._find_reachable_blocks(function)
        for block in list(function.blocks):
            if block not in reachable:
                self._remove_block(block)
                self.modified = True

    def _merge_blocks(self, function: Function) -> None:
        """Merge blocks when legal and profitable."""
        for block in list(function.blocks):
            if self._should_merge_with_successor(block):
                succ = self._get_unique_successor(block)
                if succ and self._can_merge_blocks(block, succ):
                    self._merge_blocks_internal(block, succ)
                    self.modified = True

    def _should_merge_with_successor(self, block: BasicBlock) -> bool:
        """Determine if a block should be merged with its successor."""
        # Don't merge if block has no terminator
        term = block.get_terminator()
        if not term:
            return False

        # Only consider blocks with unconditional branches
        if not isinstance(term, BranchInst) or term.is_conditional():
            return False

        # Get the successor block
        succ = self._get_unique_successor(block)
        if not succ:
            return False

        # Don't merge if successor has multiple predecessors
        if len(self._get_predecessors(succ)) > 1:
            return False

        # Don't merge if either block is a landing pad
        if self._is_landing_pad(block) or self._is_landing_pad(succ):
            return False

        return True

    def _get_unique_successor(self, block: BasicBlock) -> Optional[BasicBlock]:
        """Get the unique successor of a block if it exists."""
        term = block.get_terminator()
        if not term:
            return None

        if isinstance(term, BranchInst):
            if term.is_conditional():
                return None
            return term.target

        return None

    def _can_merge_blocks(self, pred: BasicBlock, succ: BasicBlock) -> bool:
        """Check if two blocks can be legally merged."""
        # Don't merge if predecessor ends with a potentially throwing instruction
        if self._has_throwing_instructions(pred):
            return False

        # Don't merge if successor begins with PHI nodes
        if self._has_phi_nodes(succ):
            return False

        # Don't merge if it would create a critical edge
        if self._would_create_critical_edge(pred, succ):
            return False

        # Check size constraints
        if not self._within_size_limits(pred, succ):
            return False

        return True

    def _merge_blocks_internal(self, pred: BasicBlock, succ: BasicBlock) -> None:
        """Perform the actual merging of two blocks."""
        # Remove the terminator from predecessor
        pred.get_terminator().erase_from_parent()

        # Move all instructions from successor to predecessor
        for inst in list(succ.instructions):
            inst.remove_from_parent()
            pred.append(inst)
            self._update_instruction_parent(inst, pred)

        # Update PHI nodes in successor's successors
        for next_block in self._get_successors(succ):
            self._update_phi_nodes(next_block, succ, pred)

        # Remove the successor block
        self._remove_block(succ)

    def _has_throwing_instructions(self, block: BasicBlock) -> bool:
        """Check if block contains instructions that might throw exceptions."""
        for inst in block.instructions:
            if isinstance(inst, (LoadInst, StoreInst, AllocaInst)):
                # Memory operations might throw
                return True
            if isinstance(inst, BinaryInst):
                # Division and remainder might throw
                if inst.opname in {'sdiv', 'udiv', 'srem', 'urem'}:
                    return True
        return False

    def _has_phi_nodes(self, block: BasicBlock) -> bool:
        """Check if block begins with PHI nodes."""
        return any(isinstance(inst, PhiInst) for inst in block.instructions)

    def _would_create_critical_edge(self, pred: BasicBlock, succ: BasicBlock) -> bool:
        """Check if merging would create a critical edge."""
        # A critical edge is an edge from a block with multiple successors
        # to a block with multiple predecessors
        pred_succs = self._get_successors(pred)
        succ_preds = self._get_predecessors(succ)

        return len(pred_succs) > 1 and len(succ_preds) > 1

    def _within_size_limits(self, pred: BasicBlock, succ: BasicBlock) -> bool:
        """Check if merged block would be within reasonable size limits."""
        # LLVM uses a threshold of 60 instructions for aggressive optimization
        MAX_MERGED_INSTRUCTIONS = 60
        total_instructions = len(pred.instructions) + len(succ.instructions)
        return total_instructions <= MAX_MERGED_INSTRUCTIONS

    def _update_instruction_parent(self, inst: Instruction, new_parent: BasicBlock) -> None:
        """Update the parent block of an instruction."""
        inst.parent = new_parent

    def _update_phi_nodes(self, block: BasicBlock, old_pred: BasicBlock, new_pred: BasicBlock) -> None:
        """Update PHI nodes in a block to reflect the merged predecessor."""
        for inst in block.instructions:
            if isinstance(inst, PhiInst):
                self._update_phi_node(inst, old_pred, new_pred)

    def _update_phi_node(self, phi: PhiInst, old_block: BasicBlock, new_block: BasicBlock) -> None:
        """Update a single PHI node's incoming blocks."""
        for i, (value, block) in enumerate(phi.incoming):
            if block == old_block:
                phi.incoming[i] = (value, new_block)

    def _get_successors(self, block: BasicBlock) -> List[BasicBlock]:
        """Get all successor blocks of a given block."""
        term = block.get_terminator()
        if not term:
            return []

        if isinstance(term, BranchInst):
            if term.is_conditional():
                return [term.true_dest, term.false_dest]
            return [term.target]
        elif isinstance(term, ReturnInst):
            return []

        return []

    def _get_predecessors(self, block: BasicBlock) -> List[BasicBlock]:
        """Get all predecessor blocks of a given block."""
        preds = []
        for potential_pred in block.parent.blocks:
            if block in self._get_successors(potential_pred):
                preds.append(potential_pred)
        return preds

    def _is_landing_pad(self, block: BasicBlock) -> bool:
        """Check if block is an exception handling landing pad."""
        # Check for landing pad marker instruction at start of block
        if not block.instructions:
            return False
        first_inst = block.instructions[0]
        return isinstance(first_inst, LoadInst) and first_inst.name == "landingpad"

    def _remove_block(self, block: BasicBlock) -> None:
        """Remove a basic block from its parent function."""
        if block in block.parent.blocks:
            block.parent.blocks.remove(block)

    def _eliminate_dead_switches(self, function: Function) -> None:
        """Simplify switch instructions with constant conditions."""
        for block in function.blocks:
            term = block.get_terminator()
            if isinstance(term, SwitchInst) and isinstance(term.condition, Constant):
                self._simplify_switch(block, term)
                self.modified = True

    def _simplify_jumps(self, function: Function) -> None:
        """Eliminate redundant jumps and simplify conditional branches."""
        for block in list(function.blocks):
            if self._simplify_branch(block):
                self.modified = True

    def _hoist_common_code(self, function: Function) -> None:
        """Hoist common instructions from successors to predecessor."""
        for block in list(function.blocks):
            successors = self._get_successors(block)
            if len(successors) > 1:
                common = self._find_common_instructions(successors)
                if common:
                    self._hoist_instructions(block, common)
                    self.modified = True

    def _combine_duplicate_blocks(self, function: Function) -> None:
        """Combine blocks with identical instructions."""
        block_hashes = self._compute_block_hashes(function)
        for hash_value, blocks in block_hashes.items():
            if len(blocks) > 1:
                self._merge_identical_blocks(blocks)
                self.modified = True

    def _simplify_terminator_instructions(self, function: Function) -> None:
        """Simplify various terminator instruction patterns."""
        for block in list(function.blocks):
            term = block.get_terminator()
            if isinstance(term, BranchInst):
                if term.is_conditional():
                    if isinstance(term.condition, Constant):
                        # Convert to unconditional branch
                        new_dest = term.true_dest if term.condition.value else term.false_dest
                        new_branch = BranchInst(new_dest)
                        term.replace_with(new_branch)
                        self.modified = True
                    elif self._is_condition_invertible(term.condition):
                        # Try to simplify complex conditions
                        self._simplify_condition(term)
                        self.modified = True

    def _find_common_instructions(self, blocks: List[BasicBlock]) -> List[Instruction]:
        """Find common instructions at the start of successor blocks."""
        if not blocks:
            return []

        common = []
        instructions = [block.instructions for block in blocks]
        min_length = min(len(insts) for insts in instructions)

        for idx in range(min_length):
            inst_set = {insts[idx] for insts in instructions}
            if len(inst_set) == 1 and self._can_hoist_instruction(inst_set.pop()):
                common.append(inst_set.pop())
            else:
                break

        return common

    def _can_hoist_instruction(self, inst: Instruction) -> bool:
        """Check if an instruction can be safely hoisted."""
        if isinstance(inst, (LoadInst, StoreInst, CallInst)):
            return False
        return not self._has_side_effects(inst)

    def _has_side_effects(self, inst: Instruction) -> bool:
        """Check if instruction has side effects."""
        if isinstance(inst, CallInst):
            return True
        if isinstance(inst, StoreInst):
            return True
        return False

    def _compute_block_hashes(self, function: Function) -> Dict[int, List[BasicBlock]]:
        """Compute hashes for blocks to identify duplicates."""
        block_hashes = {}
        for block in function.blocks:
            hash_value = self._compute_block_hash(block)
            if hash_value not in block_hashes:
                block_hashes[hash_value] = []
            block_hashes[hash_value].append(block)
        return block_hashes

    def _compute_block_hash(self, block: BasicBlock) -> int:
        """Compute a hash value for a block's contents."""
        hash_value = 0
        for inst in block.instructions:
            hash_value = hash_value * 31 + hash(str(inst))
        return hash_value

    def _merge_identical_blocks(self, blocks: List[BasicBlock]) -> None:
        """Merge blocks with identical instructions."""
        target = blocks[0]
        for block in blocks[1:]:
            self._redirect_predecessors(block, target)
            self._remove_block(block)

    def _redirect_predecessors(self, old_block: BasicBlock, new_block: BasicBlock) -> None:
        """Redirect all predecessors of old_block to new_block."""
        for pred in self._get_predecessors(old_block):
            term = pred.get_terminator()
            if isinstance(term, BranchInst):
                if term.is_conditional():
                    if term.true_dest == old_block:
                        term.true_dest = new_block
                    if term.false_dest == old_block:
                        term.false_dest = new_block
                else:
                    term.target = new_block

    def _is_condition_invertible(self, condition: Value) -> bool:
        """Check if a condition can be inverted."""
        if isinstance(condition, CompareInst):
            return True
        if isinstance(condition, BinaryInst):
            return condition.opname in {'and', 'or', 'xor'}
        return False

    def _simplify_condition(self, branch: BranchInst) -> None:
        """Try to simplify a complex condition."""
        condition = branch.condition
        if isinstance(condition, CompareInst):
            # Try to simplify comparison
            if self._can_invert_comparison(condition):
                new_condition = self._invert_comparison(condition)
                branch.condition = new_condition
                branch.true_dest, branch.false_dest = branch.false_dest, branch.true_dest
    def _simplify_switch(self, block: BasicBlock, switch_inst: SwitchInst) -> None:
        """Simplify switch instruction with constant condition."""
        condition = switch_inst.condition
        if not isinstance(condition, Constant):
            return

        # Find the case that matches the constant condition
        target_block = switch_inst.default
        constant_value = condition.value

        for case_value, case_block in switch_inst.cases:
            if isinstance(case_value, Constant) and case_value.value == constant_value:
                target_block = case_block
                break

        # Replace switch with direct branch
        new_branch = BranchInst(target_block)
        switch_inst.replace_with(new_branch)

        # Remove unreachable cases
        for _, case_block in switch_inst.cases:
            if case_block != target_block:
                self._mark_block_dead(case_block)

        if switch_inst.default != target_block:
            self._mark_block_dead(switch_inst.default)

        self.modified = True

    def _simplify_branch(self, block: BasicBlock) -> bool:
        """Simplify branch instructions through various optimizations."""
        term = block.get_terminator()
        if not isinstance(term, BranchInst):
            return False

        modified = False

        if term.is_conditional():
            modified |= self._simplify_conditional_branch(block, term)
        else:
            modified |= self._simplify_unconditional_branch(block, term)

        return modified

    def _simplify_conditional_branch(self, block: BasicBlock, branch: BranchInst) -> bool:
        """Simplify conditional branch instruction."""
        modified = False

        # Case 1: Constant condition
        if isinstance(branch.condition, Constant):
            target = branch.true_dest if branch.condition.value else branch.false_dest
            new_branch = BranchInst(target)
            branch.replace_with(new_branch)

            # Mark the non-taken path as dead
            other_target = branch.false_dest if branch.condition.value else branch.true_dest
            self._mark_block_dead(other_target)

            return True

        # Case 2: Both destinations are the same
        if branch.true_dest == branch.false_dest:
            new_branch = BranchInst(branch.true_dest)
            branch.replace_with(new_branch)
            return True

        # Case 3: Thread jumps through empty blocks
        true_dest = self._skip_empty_blocks(branch.true_dest)
        false_dest = self._skip_empty_blocks(branch.false_dest)

        if true_dest != branch.true_dest or false_dest != branch.false_dest:
            new_branch = BranchInst(condition=branch.condition,
                                    true_dest=true_dest,
                                    false_dest=false_dest)
            branch.replace_with(new_branch)
            modified = True

        # Case 4: Simplify based on predecessor's condition
        if self._can_simplify_based_on_predecessor(block, branch):
            modified |= self._simplify_branch_using_predecessor(block, branch)

        return modified

    def _simplify_unconditional_branch(self, block: BasicBlock, branch: BranchInst) -> bool:
        """Simplify unconditional branch instruction."""
        target = branch.target

        # Skip chains of empty blocks
        new_target = self._skip_empty_blocks(target)
        if new_target != target:
            new_branch = BranchInst(new_target)
            branch.replace_with(new_branch)
            return True

        # Remove redundant branch to next block
        if self._is_fallthrough_block(block, target):
            branch.erase_from_parent()
            return True

        return False

    def _skip_empty_blocks(self, block: BasicBlock) -> BasicBlock:
        """Skip through chains of empty blocks with unconditional branches."""
        current = block
        visited = set()

        while current and current not in visited:
            visited.add(current)

            if not self._is_empty_block(current):
                break

            term = current.get_terminator()
            if not isinstance(term, BranchInst) or term.is_conditional():
                break

            current = term.target

        return current if current not in visited else block

    def _is_empty_block(self, block: BasicBlock) -> bool:
        """Check if block is empty except for terminator."""
        return len(block.instructions) == 1 and isinstance(block.get_terminator(), BranchInst)

    def _is_fallthrough_block(self, block: BasicBlock, target: BasicBlock) -> bool:
        """Check if target block immediately follows the current block."""
        blocks = block.parent.blocks
        try:
            current_idx = blocks.index(block)
            return current_idx + 1 < len(blocks) and blocks[current_idx + 1] == target
        except ValueError:
            return False

    def _can_simplify_based_on_predecessor(self, block: BasicBlock, branch: BranchInst) -> bool:
        """Check if branch can be simplified based on predecessor's condition."""
        preds = self._get_predecessors(block)
        if len(preds) != 1:
            return False

        pred = preds[0]
        pred_term = pred.get_terminator()
        if not isinstance(pred_term, BranchInst) or not pred_term.is_conditional():
            return False

        return self._are_conditions_related(pred_term.condition, branch.condition)

    def _simplify_branch_using_predecessor(self, block: BasicBlock, branch: BranchInst) -> bool:
        """Simplify branch using predecessor's condition."""
        pred = self._get_predecessors(block)[0]
        pred_term = pred.get_terminator()
        pred_cond = pred_term.condition

        # If the conditions are identical or inverse
        if self._are_identical_conditions(pred_cond, branch.condition):
            # Conditions are the same, take the same path
            new_branch = BranchInst(branch.true_dest)
            branch.replace_with(new_branch)
            return True
        elif self._are_inverse_conditions(pred_cond, branch.condition):
            # Conditions are opposite, take the opposite path
            new_branch = BranchInst(branch.false_dest)
            branch.replace_with(new_branch)
            return True

        return False

    def _are_conditions_related(self, cond1: Value, cond2: Value) -> bool:
        """Check if two conditions are related (identical or inverse)."""
        return self._are_identical_conditions(cond1, cond2) or self._are_inverse_conditions(cond1, cond2)

    def _are_identical_conditions(self, cond1: Value, cond2: Value) -> bool:
        """Check if two conditions are identical."""
        if isinstance(cond1, CompareInst) and isinstance(cond2, CompareInst):
            return (cond1.opname == cond2.opname and
                    cond1.operands[0] == cond2.operands[0] and
                    cond1.operands[1] == cond2.operands[1])
        return cond1 == cond2

    def _are_inverse_conditions(self, cond1: Value, cond2: Value) -> bool:
        """Check if two conditions are logical inverses."""
        if not isinstance(cond1, CompareInst) or not isinstance(cond2, CompareInst):
            return False

        inverse_ops = {
            'eq': 'ne',
            'ne': 'eq',
            'slt': 'sge',
            'sle': 'sgt',
            'sgt': 'sle',
            'sge': 'slt',
            'ult': 'uge',
            'ule': 'ugt',
            'ugt': 'ule',
            'uge': 'ult'
        }

        return (cond1.opname == inverse_ops.get(cond2.opname, '') and
                cond1.operands[0] == cond2.operands[0] and
                cond1.operands[1] == cond2.operands[1])

    def _mark_block_dead(self, block: BasicBlock) -> None:
        """Mark a block as dead for later cleanup."""
        if not hasattr(self, '_dead_blocks'):
            self._dead_blocks = set()
        self._dead_blocks.add(block)

    def _cleanup_dead_blocks(self, function: Function) -> None:
        """Remove all blocks marked as dead."""
        if hasattr(self, '_dead_blocks'):
            for block in self._dead_blocks:
                if block in function.blocks:
                    self._remove_block(block)
            self._dead_blocks.clear()