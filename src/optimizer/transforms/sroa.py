import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.optimizer.analyzers.cfgnode import CFGNode
from src.optimizer.analyzers.domtree import DomTree
from src.optimizer.analyzers.ssa import SSA


class SROATransform:

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        """Transform each function in the module."""
        for constructor in module.constructors:
            SROAFunctionTransform.transform(constructor)
        for global_value in module.globals:
            if isinstance(global_value, hir_values.Function) and len(global_value.blocks) > 0:
                SROAFunctionTransform.transform(global_value)
        return module

class SROAFunctionTransform:

    def __init__(self):
        self.phis = {}
        self.geps = {}

    @staticmethod
    def transform(function: hir_values.Function):
        transformer = SROAFunctionTransform()
        transformer.__insert_phis(function)
        transformer.__rename(function)
        transformer.__clear_useless_phis(function)

    def __clear_useless_phis(self, function: hir_values.Function):
        changed = True
        while changed:
            changed = False
            instruction_to_remove, value = SROAFunctionTransform.__find_first_useless_phi(function)
            if instruction_to_remove is not None:
                changed = True
                for block in function.blocks:
                    block.replace_instruction(instruction_to_remove, value)

    @staticmethod
    def __find_first_useless_phi(function: hir_values.Function):
        for block in function.blocks:
            for instr in block.instructions:
                if isinstance(instr, hir_instructions.PhiInstruction):
                    vals = set()
                    for inc in instr.incomings:
                        vals.add(inc[0])
                    if len(vals) == 1:
                        return instr, next(iter(vals))
        return None, None

    def __rename(self, function: hir_values.Function):
        st = [(function.blocks[0], {})]
        candidates = self.__find_candidates(function)
        dom_tree = DomTree.dom(function)
        cfg_nodes = CFGNode.build_nodes(function)
        while len(st) > 0:
            (block, alloca_scalars), st = st[0], st[1:]

            #Attemp to propagate scalars
            instr_to_remove = []
            for idx, instr in enumerate(block.instructions):
                if isinstance(instr, hir_instructions.AllocateInstruction) and instr in candidates:
                    alloca_scalars[instr] = hir_values.HirDefaultValues.get(instr.allocated_type)
                elif isinstance(instr, hir_instructions.StoreInstruction) and instr.operands[1] in candidates:
                    alloca_scalars[instr.operands[1]] = instr.operands[0]
                    instr_to_remove.append(idx)
                elif isinstance(instr, hir_instructions.LoadInstruction) and instr.operands[0] in candidates:
                    block.replace_instruction(instr, alloca_scalars[instr.operands[0]], remove_old=False)
                    instr_to_remove.append(idx)
                elif isinstance(instr, hir_instructions.PhiInstruction) and self.phis[instr] in candidates:
                    alloca_scalars[self.phis[instr]] = instr

            cleared_instructions = []
            for idx in range(len(block.instructions)):
                if idx not in instr_to_remove:
                    cleared_instructions.append(block.instructions[idx])
            block.instructions = cleared_instructions
            # Replacing phis in successors
            for succ in cfg_nodes[block].children:
                for instr in succ.instructions:
                    if isinstance(instr, hir_instructions.PhiInstruction) and self.phis[instr] in candidates:
                        if self.phis[instr] in alloca_scalars and instr != alloca_scalars[self.phis[instr]]:
                            #print(f"Added ({alloca_scalars[instr.metadata]}, {block.name}) to {instr}")
                            instr.add_incoming(alloca_scalars[self.phis[instr]], block)

            # Iterating over the dominance tree
            for child in dom_tree[block]:
                st.append((child, alloca_scalars.copy()))

        # Removing useless allocas from blocks
        for block in function.blocks:
            for alloca in candidates:
                if alloca in block.instructions:
                    block.instructions.remove(alloca)
        cnt = 0
        # Rename remaining values
        for block in function.blocks:
            for instr in block.instructions:
                if instr.name != hir_values.NamedValue.empty_name:
                    instr.name = f"{cnt}"
                    cnt += 1

    def __insert_phis(self, function: hir_values.Function):
        candidates = self.__find_candidates(function)
        dom_frontier = DomTree.dom_front(function)
        WL = []
        alloca_scalars = {}
        alloca_phi = {}
        for alloca in candidates:
            alloca_scalars[alloca] = {}
            alloca_phi[alloca] = {}
            for block in function.blocks:
                if self.__is_defined(function, block, alloca):
                    alloca_phi[alloca][block] = None
                    WL.append(block)
            while len(WL) > 0:
                def_block, WL = WL[0], WL[1:]
                for block in dom_frontier[def_block]:
                    if alloca_phi[alloca][block] is None:
                        phi_instr = hir_instructions.PhiInstruction(block, alloca.allocated_type)
                        self.phis[phi_instr] = alloca
                        block.instructions.insert(0, phi_instr)
                        alloca_phi[alloca][block] = phi_instr
                        WL.append(block)

    def __is_defined(self, function: hir_values.Function, block: hir_values.Block, alloca_instr: hir_instructions.AllocateInstruction):
        cfg_nodes = CFGNode.build_nodes(function)
        visited = set()
        st = [block]
        while len(st) > 0:
            current, st = st[0], st[1:]
            if current is alloca_instr.parent:
                return True
            if current not in visited:
                visited.add(block)
                st += cfg_nodes[current].parents
        return False
        #return alloca_instr.parent in dom_set[block]

    def __find_candidates(self, function: hir_values.Function):
        """Find allocas that are candidates for SROA."""
        candidates = []

        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, hir_instructions.AllocateInstruction):
                    if not isinstance(inst.allocated_type, hir_types.StructType) and self._is_sroa_candidate(function, inst):
                        candidates.append(inst)

        return candidates

    def _is_sroa_candidate(self, function: hir_values.Function, alloca: hir_instructions.AllocateInstruction) -> bool:
        for use in self._get_uses(function, alloca):
            if not self._is_safe_use(use):
                return False
        return True

    def _is_safe_use(self, inst: hir_instructions.Instruction) -> bool:
        return isinstance(inst, (hir_instructions.LoadInstruction, hir_instructions.StoreInstruction))

    def _get_uses(self, function: hir_values.Function, inst: hir_instructions.Instruction):
        result = []
        for block in function.blocks:
            for instruction in block.instructions:
                if inst in instruction.operands:
                    result.append(instruction)
        return result
