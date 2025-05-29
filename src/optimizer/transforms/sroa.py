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
        for global_value in module.globals:
            if isinstance(global_value, hir_values.Function):
                SROAFunctionTransform.transform(global_value)
        return module

class SROAFunctionTransform:
    @staticmethod
    def transform(function: hir_values.Function):
        """Apply SROA to a single function."""
        candidates = SROAFunctionTransform.__find_candidates(function)

        for alloca in candidates:
            self._promote_alloca(function, alloca)

    @staticmethod
    def __find_candidates(function: hir_values.Function):
        """Find allocas that are candidates for SROA."""
        candidates = []

        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, hir_instructions.AllocateInstruction):
                    if SROAFunctionTransform._is_sroa_candidate(function, inst):
                        candidates.append(inst)

        return candidates

    @staticmethod
    def _is_sroa_candidate(function: hir_values.Function, alloca: hir_instructions.AllocateInstruction) -> bool:
        """Check if an alloca instruction is eligible for SROA."""
        # Check all uses
        for use in SROAFunctionTransform._get_uses(function, alloca):
            if not SROAFunctionTransform._is_safe_use(use):
                return False
        return True

    @staticmethod
    def _is_safe_use(inst: hir_instructions.Instruction) -> bool:
        """Determine if an instruction's use of an aggregate is safe for SROA."""
        if isinstance(inst, (hir_instructions.LoadInstruction, hir_instructions.StoreInstruction)):
            return True
        if isinstance(inst, hir_instructions.GEPInstruction):
            return all(isinstance(idx, hir_values.ConstantValue) for idx in inst.indices[1:])
        return False

    @staticmethod
    def _get_uses(function: hir_values.Function, inst: hir_instructions.Instruction):
        result = []
        for block in function.blocks:
            for instruction in block.instructions:
                if inst in instruction.operands:
                    result.append(instruction)
        return result

    @staticmethod
    def _promote_alloca(function: hir_values.Function, alloca: hir_instructions.AllocateInstruction) -> None:
        """Convert an aggregate alloca into scalar variables."""
        scalar_values = SROAFunctionTransform._create_scalar_allocas(function, alloca)
        self._rewrite_uses(alloca, scalar_values)
        self._remove_original_alloca(alloca)
        self.modified = True

    @staticmethod
    def _create_scalar_allocas(function: hir_values.Function, alloca: hir_instructions.AllocateInstruction):
        """Create scalar allocas for each field of the aggregate."""
        scalar_values = {}
        aggregate_type = alloca.type.pointee

        if isinstance(aggregate_type, StructType):
            for idx, field_type in enumerate(aggregate_type.field_types):
                name = f"{alloca.name}.field{idx}"
                new_alloca = self._create_alloca(function, field_type, name)
                scalar_values[idx] = new_alloca

        elif isinstance(aggregate_type, ArrayType):
            element_type = aggregate_type.element_type
            for idx in range(aggregate_type.size):
                name = f"{alloca.name}.element{idx}"
                new_alloca = self._create_alloca(function, element_type, name)
                scalar_values[idx] = new_alloca

        return scalar_values