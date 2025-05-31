import enum
from collections import defaultdict
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.hir.instructions import PhiInstruction
from src.optimizer.analyzers.cfgnode import CFGNode
from src.optimizer.analyzers.domtree import DomTree
from src.optimizer.analyzers.ssa import SSA
from src.optimizer.transforms.dce import DCEFunctionTransform

class GVNTransform:

    def __init__(self):
        self.partition = defaultdict(set)
        self.cnt = 0

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        transformer = GVNTransform()
        for global_value in module.globals:
            if isinstance(global_value, hir_values.Function) and len(global_value.blocks) > 0:
                GVNFunctionTransform.transform(global_value)
            elif isinstance(global_value, hir_values.GlobalVariable):
                transformer.partition[f"{global_value.value_type}"].add(global_value)
        transformer.__split()
        for key, val in transformer.partition.items():
            packet = list(val)
            if len(packet) > 1:
                instruction = GVNTransform.__find_earliest_instruction(module, packet)
                packet.remove(instruction)
                for global_value in module.globals:
                    if isinstance(global_value, hir_values.Function) and len(global_value.blocks) > 0:
                        for block in global_value.blocks:
                            for instr in packet:
                                block.replace_instruction(instr, instruction)
                for instr in packet:
                    module.globals.remove(instr)
        return module

    @staticmethod
    def __find_earliest_instruction(module, instructions):
        result = None
        result_idx = -1
        for instr in instructions:
            if instr in module.globals:
                if module.globals.index(instr) < result_idx or result_idx == -1:
                    result = instr
                    result_idx = module.globals.index(instr)
        return result

    def __split(self):
        changed = True
        while changed:
            changed = False
            new_partition = defaultdict(set)
            cnt = 0
            for key, value in self.partition.items():
                packet = value.copy()
                instr = packet.pop()
                packetI, packetNonI = set(), set()
                packetI.add(instr)
                while len(packet) > 0:
                    j = packet.pop()
                    if self.__match(instr, j):
                        packetI.add(j)
                    else:
                        packetNonI.add(j)
                new_partition[cnt] = packetI
                cnt += 1
                if len(packetNonI) > 0:
                    new_partition[cnt] = packetNonI
                    cnt += 1
                    changed = True
            self.partition = new_partition

    def __match(self, instr1, instr2):
        if isinstance(instr1.init_value, hir_values.ConstantValue) and isinstance(instr2.init_value, hir_values.ConstantValue):
            return instr1.init_value.value == instr2.init_value.value

    def __find_key(self, instr):
        for key, set in self.partition.items():
            if instr in set:
                return key
        return None

class GVNFunctionTransform:
    OPERATIONS = {
        'add': '+',
        'fadd': '+',
        'sub': '-',
        'fsub': '-',
        'mul': '*',
        'fmul': '-',
        'sdiv': '/',
        'fdiv': '/',
        'fneg': '-',
        'zext': 'zext',
        'sitofp': 'sitofp',
        'fpext': 'fpext',
    }

    def __init__(self, function: hir_values.Function):
        self.partition = self.__init_partition(function)
        self.cnt = 0

    @staticmethod
    def transform(function: hir_values.Function):
        dom = DomTree.dom(function)
        cfg_node = CFGNode.build_nodes(function)
        transformer = GVNFunctionTransform(function)
        transformer.__split(function)
        for key, val in transformer.partition.items():
            packet = list(val)
            if len(packet) > 1:
                st = [(function.blocks[0], None)]
                while len(st) > 0:
                    (current, value), st = st[0], st[1:]
                    if value is None:
                        instruction = GVNFunctionTransform.__find_earliest_instruction(current, packet)
                        if instruction is not None:
                            value = instruction
                    if value is not None:
                        for instr in packet:
                            if instr != value:
                                current.replace_instruction(instr, value)
                                for succ in cfg_node[current].children:
                                    succ.replace_instruction(instr, value)
                    st += [(block, value) for block in dom[current]]
                """
                closest = GVNFunctionTransform.__find_closest_block(function, dom, packet)
                instruction = GVNFunctionTransform.__find_earliest_instruction(closest, packet)
                packet.remove(instruction)
                for block in function.blocks:
                    for instr in packet:
                        block.replace_instruction(instr, instruction)
                """
        return function

    @staticmethod
    def __find_earliest_instruction(block, instructions):
        result = None
        result_idx = -1
        for instr in instructions:
            if instr in block.instructions:
                if block.instructions.index(instr) < result_idx or result_idx == -1:
                    result = instr
                    result_idx = block.instructions.index(instr)
        return result

    @staticmethod
    def __find_closest_block(function, dom, instructions):
        st = [function.blocks[0]]
        while len(st) > 0:
            current, st = st[0], st[1:]
            for instr in instructions:
                if instr in current.instructions:
                    return current
            st += dom[current]
        return None

    def __split(self, function: hir_values.Function):
        changed = True
        while changed:
            changed = False
            new_partition = defaultdict(set)
            cnt = 0
            for key, value in self.partition.items():
                packet = value.copy()
                instr = packet.pop()
                packetI, packetNonI = set(), set()
                packetI.add(instr)
                while len(packet) > 0:
                    j = packet.pop()
                    if self.__match(instr, j):
                        packetI.add(j)
                    else:
                        packetNonI.add(j)
                new_partition[cnt] = packetI
                cnt += 1
                if len(packetNonI) > 0:
                    new_partition[cnt] = packetNonI
                    cnt += 1
                    changed = True
            self.partition = new_partition

    def __match(self, instr1, instr2):
        if isinstance(instr1, hir_instructions.PhiInstruction):
            result = True
            for inc1, inc2 in zip(instr1.incomings, instr2.incomings):
                result &= inc1[0] == inc2[0] or self.__find_key(inc1[0]) == self.__find_key(inc2[0])
            return result and instr1.parent is instr2.parent
        elif isinstance(instr1, hir_values.GlobalVariable):
            return False
        elif isinstance(instr1, hir_instructions.AllocateInstruction):
            return False
        elif isinstance(instr1, hir_instructions.GEPInstruction):
            result = True
            for idx1, idx2 in zip(instr1.operands[1:], instr2.operands[1:]):
                if isinstance(idx1, hir_values.ConstantValue) and isinstance(idx2, hir_values.ConstantValue):
                    result &= idx1.value == idx2.value
                else:
                    result &= self.__find_key(idx1) == self.__find_key(idx2)
            return self.__find_key(instr1.operands[0]) == self.__find_key(instr2.operands[0]) and result
        elif instr1.opname == 'add' or instr1.opname == 'fadd' or instr1.opname == 'mul' or instr1.opname == 'fmul':
            lhs_constants = set([op.value for op in instr1.operands if isinstance(op, hir_values.ConstantValue)])
            rhs_constants = set([op.value for op in instr2.operands if isinstance(op, hir_values.ConstantValue)])
            lhs = set([self.__find_key(oper) for oper in instr1.operands])
            rhs = set([self.__find_key(oper) for oper in instr2.operands])
            return lhs == rhs and lhs_constants == rhs_constants
        else:
            result = True
            for idx1, idx2 in zip(instr1.operands, instr2.operands):
                if isinstance(idx1, hir_values.ConstantValue) and isinstance(idx2, hir_values.ConstantValue):
                    result &= idx1.value == idx2.value
                else:
                    result &= self.__find_key(idx1) == self.__find_key(idx2)
            return result

    def __init_partition(self, function: hir_values.Function):
        self.partition = defaultdict(set)
        for global_values in function.parent.globals:
            if isinstance(global_values, hir_values.Function):
                self.partition[global_values.name].add(global_values)
            elif isinstance(global_values, hir_values.GlobalVariable):
                self.partition[f"{global_values.value_type}"].add(global_values)
        for arg in function.args:
            self.partition[arg.name].add(arg)
        for block in function.blocks:
            for instr in block.instructions:
                if isinstance(instr, hir_instructions.Terminator):
                    continue
                elif isinstance(instr, hir_instructions.CallInstruction) and isinstance(instr.type, hir_types.VoidType):
                    continue
                elif isinstance(instr, hir_instructions.StoreInstruction):
                    continue
                if isinstance(instr, hir_instructions.PhiInstruction):
                    self.partition['phi'].add(instr)
                elif isinstance(instr, hir_instructions.SelectInstruction):
                    self.partition['select'].add(instr)
                elif isinstance(instr, hir_instructions.CompareInstruction):
                    self.partition[instr.op].add(instr)
                elif instr.opname in GVNFunctionTransform.OPERATIONS:
                    self.partition[instr.opname].add(instr)
                else:
                    self.partition[instr.opname].add(instr)
        return self.partition

    def __find_key(self, instr):
        for key, set in self.partition.items():
            if instr in set:
                return key
        return None