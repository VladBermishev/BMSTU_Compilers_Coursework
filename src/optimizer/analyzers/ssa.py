import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.hir.instructions import PhiInstruction
from src.optimizer.analyzers.cfgnode import CFGNode
from src.optimizer.analyzers.domtree import DomTree


class SSA:

    @staticmethod
    def ssa_nodes(function: hir_values.Function, include_calls=False):
        result = []
        for arg in function.args:
            result.append(arg)
        for block in function.blocks:
            for instr in block.instructions:
                if include_calls and isinstance(instr, hir_instructions.CallInstruction):
                    result.append(instr)
                elif not isinstance(instr, hir_instructions.AllocateInstruction) and instr.name != hir_values.NamedValue.empty_name:
                    result.append(instr)
        return result

    @staticmethod
    def dep_graph(function):
        nodes = {}
        for ssa_node in SSA.ssa_nodes(function, include_calls=True):
            nodes[ssa_node] = set()
        for ssa_node in SSA.ssa_nodes(function, include_calls=True):
            if isinstance(ssa_node, PhiInstruction):
                for inc in ssa_node.incomings:
                    if inc[0] in nodes:
                        nodes[inc[0]].add(ssa_node)
            elif not isinstance(ssa_node, hir_values.Argument):
                for operand in ssa_node.operands:
                    if operand in nodes:
                        nodes[operand].add(ssa_node)
        return nodes

    @staticmethod
    def inverted_dep_graph(function):
        nodes = {}
        for ssa_node in SSA.ssa_nodes(function, include_calls=True):
            nodes[ssa_node] = set()
        for ssa_node in SSA.ssa_nodes(function, include_calls=True):
            if isinstance(ssa_node, PhiInstruction):
                for inc in ssa_node.incomings:
                    if inc[0] in nodes:
                        nodes[ssa_node].add(inc[0])
            elif not isinstance(ssa_node, hir_values.Argument):
                for operand in ssa_node.operands:
                    if operand in nodes:
                        nodes[ssa_node].add(operand)
        return nodes

    @staticmethod
    def ssa_uses(function: hir_values.Function, instr_to: hir_instructions.Instruction):
        result = []
        for block in function.blocks:
            for bi in block.instructions:
                if isinstance(bi, (hir_instructions.AllocateInstruction, hir_instructions.LoadInstruction)):
                    continue
                if isinstance(bi, PhiInstruction):
                    if instr_to in [inc[0] for inc in bi.incomings]:
                        result.append(instr_to)
                else:
                    if instr_to in bi.operands:
                        result.append(instr_to)
        return result
