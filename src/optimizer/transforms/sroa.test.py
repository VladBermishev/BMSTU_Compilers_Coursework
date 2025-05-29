from src.codegen.hir.hir_types import ArrayType, StructType, Type
from src.codegen.hir.hir_values import (
    Argument, BasicBlock, Constant, Function, GlobalValue,
    Instruction, LocalValue, Value
)
from src.codegen.hir.hir_module import Module
from src.codegen.hir.hir_instructions import (
    LoadInst, StoreInst, GetElementPtrInst, AllocaInst
)
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class SROATransform:
    def __init__(self):
        self.modified = False

    @staticmethod
    def transform(module: Module) -> Module:
        """Apply SROA transformation to the entire module."""
        transformer = SROATransform()
        return transformer._transform_module(module)

    def _transform_module(self, module: Module) -> Module:
        """Transform each function in the module."""
        for constructor in module.constructors:
            self._transform_function(constructor)
        return module

    def _transform_function(self, function: Function) -> None:
        """Apply SROA to a single function."""
        candidates = self._find_sroa_candidates(function)

        for alloca in candidates:
            self._promote_alloca(function, alloca)

    def _find_sroa_candidates(self, function: Function) -> List[AllocaInst]:
        """Find allocas that are candidates for SROA."""
        candidates = []

        for block in function.blocks:
            for inst in block.instructions:
                if isinstance(inst, AllocaInst):
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

    def _promote_alloca(self, function: Function, alloca: AllocaInst) -> None:
        """Convert an aggregate alloca into scalar variables."""
        scalar_values = self._create_scalar_allocas(function, alloca)
        self._rewrite_uses(alloca, scalar_values)
        self._remove_original_alloca(alloca)
        self.modified = True

    def _create_scalar_allocas(
            self, function: Function, alloca: AllocaInst
    ) -> Dict[int, AllocaInst]:
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

    def _create_alloca(
            self, function: Function, type_: Type, name: str
    ) -> AllocaInst:
        """Create a new alloca instruction."""
        entry_block = function.blocks[0]
        alloca = AllocaInst(type_, name)
        entry_block.insert_at_start(alloca)
        return alloca

    def _rewrite_uses(
            self, original: AllocaInst, scalar_values: Dict[int, AllocaInst]
    ) -> None:
        """Rewrite all uses of the original aggregate with scalar operations."""
        uses = list(self._get_uses(original))

        for use in uses:
            if isinstance(use, LoadInst):
                self._rewrite_load(use, scalar_values)
            elif isinstance(use, StoreInst):
                self._rewrite_store(use, scalar_values)
            elif isinstance(use, GetElementPtrInst):
                self._rewrite_gep(use, scalar_values)

    def _rewrite_load(
            self, load: LoadInst, scalar_values: Dict[int, AllocaInst]
    ) -> None:
        """Rewrite a load from an aggregate into loads from scalar values."""
        if isinstance(load.ptr, GetElementPtrInst):
            # Loading a specific field/element
            idx = self._get_constant_index(load.ptr)
            if idx is not None:
                new_load = LoadInst(scalar_values[idx])
                load.replace_all_uses_with(new_load)
                load.erase_from_parent()

    def _rewrite_store(
            self, store: StoreInst, scalar_values: Dict[int, AllocaInst]
    ) -> None:
        """Rewrite a store to an aggregate into stores to scalar values."""
        if isinstance(store.ptr, GetElementPtrInst):
            # Storing to a specific field/element
            idx = self._get_constant_index(store.ptr)
            if idx is not None:
                new_store = StoreInst(store.value, scalar_values[idx])
                store.insert_before(new_store)
                store.erase_from_parent()

    def _get_constant_index(self, gep: GetElementPtrInst) -> Optional[int]:
        """Get the constant index from a GEP instruction."""
        if len(gep.indices) == 2 and isinstance(gep.indices[1], Constant):
            return gep.indices[1].value
        return None

    def _remove_original_alloca(self, alloca: AllocaInst) -> None:
        """Remove the original aggregate alloca."""
        alloca.erase_from_parent()

    def _get_uses(self, value: Value) -> Set[Instruction]:
        """Get all instructions that use this value."""
        return {user for user in value.users if isinstance(user, Instruction)}

    def _is_sroa_candidate(self, function: hir_values.Function,
                           alloca: hir_instructions.AllocateInstruction) -> bool:
        """Проверяет, подходит ли alloca для SROA."""
        if not self._has_safe_uses(function, alloca):
            return False

        pointee_type = alloca.type.pointee

        # Проверяем базовые типы
        if isinstance(pointee_type, (NumericT, CharT, BoolT)):
            # Для скалярных типов SROA нужна только если есть множественные store
            # или если значение можно продвинуть в регистры
            return self._should_promote_scalar(function, alloca)

        # Для указателей особая обработка
        if isinstance(pointee_type, PointerT):
            return self._should_promote_pointer(function, alloca)

        # Процедурные типы не подлежат SROA
        if isinstance(pointee_type, ProcedureT):
            return False

        # Для агрегатных типов - стандартная логика
        return (isinstance(pointee_type, hir_types.StructType) or
                isinstance(pointee_type, hir_types.ArrayType))

    def _should_promote_scalar(self, function: hir_values.Function,
                               alloca: hir_instructions.AllocateInstruction) -> bool:
        """Определяет, нужно ли продвигать скалярную переменную."""
        store_count = 0
        has_complex_uses = False

        for use in self._get_uses(function, alloca):
            if isinstance(use, hir_instructions.StoreInstruction):
                store_count += 1
                if store_count > 1:
                    return True
            elif not isinstance(use, hir_instructions.LoadInstruction):
                has_complex_uses = True

        # Продвигаем если:
        # 1. Есть только один store и все остальные использования - load
        # 2. Нет сложных использований (например, взятия адреса)
        return store_count == 1 and not has_complex_uses

    def _should_promote_pointer(self, function: hir_values.Function,
                                alloca: hir_instructions.AllocateInstruction) -> bool:
        """Определяет, нужно ли продвигать указатель."""
        # Указатели продвигаем только если:
        # 1. Нет взятия адреса самого указателя
        # 2. Все использования - load/store
        for use in self._get_uses(function, alloca):
            if not isinstance(use, (hir_instructions.LoadInstruction,
                                    hir_instructions.StoreInstruction)):
                return False
        return True

    def _promote_scalar(self, function: hir_values.Function,
                        alloca: hir_instructions.AllocateInstruction):
        """Продвигает скалярную переменную в регистры."""
        value = None

        # Находим единственный store
        for use in self._get_uses(function, alloca):
            if isinstance(use, hir_instructions.StoreInstruction):
                value = use.value
                break

        if value is not None:
            # Заменяем все load на использование значения
            for use in list(self._get_uses(function, alloca)):
                if isinstance(use, hir_instructions.LoadInstruction):
                    use.replace_all_uses_with(value)
                    self._remove_instruction(function, use)
                elif isinstance(use, hir_instructions.StoreInstruction):
                    self._remove_instruction(function, use)

            # Удаляем оригинальный alloca
            self._remove_alloca(function, alloca)
            self.modified = True
