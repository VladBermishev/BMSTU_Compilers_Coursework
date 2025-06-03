import enum
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.hir.instructions import PhiInstruction
from src.optimizer.analyzers.cfgnode import CFGNode
from src.optimizer.analyzers.domtree import DomTree
from src.optimizer.analyzers.ssa import SSA
from src.optimizer.transforms.dce import DCEFunctionTransform


class SCPTransform:

    @staticmethod
    def transform(module: hir_module.Module) -> hir_module.Module:
        for global_value in module.globals:
            if isinstance(global_value, hir_values.Function) and len(global_value.blocks) > 0:
                SCPFunctionTransform.transform(global_value)
        return module

class SCPFunctionTransform:
    class SCPLatticeValue(enum.Enum):
        BOTTOM = 0
        TOP = 1
        VALUE = 2

    @staticmethod
    def transform(function: hir_values.Function):
        changed = True
        while changed:
            changed = False
            instructions_len = sum([len(block.instructions) for block in function.blocks])
            SCPFunctionTransform.__scp(function)
            DCEFunctionTransform.transform(function)
            if instructions_len != sum([len(block.instructions) for block in function.blocks]):
                changed = True

    @staticmethod
    def __scp(function: hir_values.Function):
        lattice = SCPFunctionTransform.__init_lattice(function)
        st = []
        dep_graph = SSA.dep_graph(function)
        for ssa_node, succ in dep_graph.items():
            for succ_node in succ:
                if SCPFunctionTransform.__is_const(ssa_node):
                    st.append((ssa_node, succ_node))
        while len(st) > 0:
            edge, st = st[0], st[1:]
            definition, usage = edge[0], edge[1]
            if SCPFunctionTransform.__is_const(definition):
                lattice[definition] = SCPFunctionTransform.__evaluate_constant(definition)
                usage.replace_oper(definition, lattice[definition])
            if SCPFunctionTransform.__is_const(usage):
                lattice[usage] = SCPFunctionTransform.__evaluate_constant(usage)
                for user in dep_graph[usage]:
                    st.append((usage, user))

    @staticmethod
    def __init_lattice(function: hir_values.Function):
        lattice = {}
        dep_graph = SSA.inverted_dep_graph(function)
        for ssa_node in SSA.ssa_nodes(function):
            if len(dep_graph[ssa_node]) != 0:
                lattice[ssa_node] = SCPFunctionTransform.SCPLatticeValue.BOTTOM
            elif SCPFunctionTransform.__is_const(ssa_node):
                lattice[ssa_node] = SCPFunctionTransform.__evaluate_constant(ssa_node)
            else:
                lattice[ssa_node] = SCPFunctionTransform.SCPLatticeValue.TOP
        return lattice

    @staticmethod
    def __is_const(ssa_node: hir_instructions.Instruction):
        if isinstance(ssa_node, (hir_instructions.LoadInstruction, hir_instructions.AllocateInstruction)):
            return False
        elif isinstance(ssa_node, (hir_instructions.CallInstruction, hir_instructions.ReturnInstruction)):
            return False
        elif isinstance(ssa_node, hir_values.Argument):
            return False
        if isinstance(ssa_node, hir_instructions.PhiInstruction):
            vals = set()
            for incoming in ssa_node.incomings:
                vals.add(incoming[0])
            return len(vals) == 1
        elif isinstance(ssa_node, hir_instructions.SelectInstruction):
            return isinstance(ssa_node.operands[0], hir_values.ConstantValue)
        else:
            result = all([isinstance(oper, hir_values.ConstantValue) for oper in ssa_node.operands])
            if result and (ssa_node.opname == 'sdiv' or ssa_node.opname == 'fdiv') and ssa_node.operands[1].value == 0:
                return False
            return result

    @staticmethod
    def __meet(lhs, rhs):
        if lhs == SCPFunctionTransform.SCPLatticeValue.BOTTOM or rhs == SCPFunctionTransform.SCPLatticeValue.BOTTOM:
            return SCPFunctionTransform.SCPLatticeValue.BOTTOM
        if lhs == SCPFunctionTransform.SCPLatticeValue.TOP:
            return rhs
        if rhs == SCPFunctionTransform.SCPLatticeValue.TOP:
            return lhs
        if lhs == rhs:
            return lhs
        return SCPFunctionTransform.SCPLatticeValue.BOTTOM

    @staticmethod
    def __evaluate_constant(instr: hir_instructions.Instruction):
        if isinstance(instr, hir_instructions.PhiInstruction):
            return instr.incomings[0][0].value if isinstance(instr.incomings[0][0], hir_values.ConstantValue) else instr.incomings[0][0]
        elif isinstance(instr, hir_instructions.SelectInstruction):
            return  instr.operands[1].value if instr.operands[0].value == 1 else instr.operands[2].value
        else:
            if instr.opname == 'add' or instr.opname == 'fadd':
                return hir_values.ConstantValue(instr.type, instr.operands[0].value + instr.operands[1].value)
            elif instr.opname == 'sub' or instr.opname == 'fsub':
                return hir_values.ConstantValue(instr.type, instr.operands[0].value - instr.operands[1].value)
            elif instr.opname == 'mul' or instr.opname == 'fmul':
                return hir_values.ConstantValue(instr.type, instr.operands[0].value * instr.operands[1].value)
            elif instr.opname == 'sdiv' or instr.opname == 'fdiv':
                return hir_values.ConstantValue(instr.type, instr.operands[0].value / instr.operands[1].value)
            elif instr.opname == 'fneg':
                return hir_values.ConstantValue(instr.type, -instr.operands[0].value)
            elif instr.opname == 'zext' or instr.opname == 'sitofp' or instr.opname == 'fpext':
                return hir_values.ConstantValue(instr.type, instr.operands[0].value)
            elif isinstance(instr, hir_instructions.CompareInstruction):
                opname = instr.op[-2] + instr.op[-1]
                op = hir_instructions.CompareInstruction.OP_MAP[opname]
                result = eval(f"{instr.operands[0].value} {op} {instr.operands[1].value}")
                return hir_values.ConstantValue(hir_types.BoolType(), 1 if result else 0)

        raise ValueError("Unexpected instruction")
