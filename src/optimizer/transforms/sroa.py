import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions

class SROATransform:

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        """Transform each function in the module."""
        for constructor in module.constructors:
            SROAFunctionTransform.transform(constructor)
        for constructor in module.globals:
            SROAFunctionTransform.transform(constructor)
        return module

class SROAFunctionTransform:
    @staticmethod
    def transform(function: hir_values.Function):
        """Apply SROA to a single function."""
        candidates = SROAFunctionTransform.__find_candidates(function)

        for alloca in candidates:
            self._promote_alloca(function, alloca)

    def __find_candidates(self, function: hir_values.Function):
        """Find allocas that are candidates for SROA."""
        candidates = []

        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, hir_instructions.AllocateInstruction):
                    if self._is_sroa_candidate(inst):
                        candidates.append(inst)

        return candidates

    def _is_sroa_candidate(self, alloca: AllocaInst) -> bool:
        """Check if an alloca instruction is eligible for SROA."""
        # Must be an aggregate type
        if not isinstance(alloca.type.pointee, (ArrayType, StructType)):
            return False

        # Check all uses
        for use in self._get_uses(alloca):
            if not self._is_safe_use(use):
                return False

        return True

    def _is_safe_use(self, inst: Instruction) -> bool:
        """Determine if an instruction's use of an aggregate is safe for SROA."""
        if isinstance(inst, LoadInst):
            return True
        if isinstance(inst, StoreInst):
            return True
        if isinstance(inst, GetElementPtrInst):
            # Only allow simple field/element access
            return all(isinstance(idx, Constant) for idx in inst.indices[1:])
        return False