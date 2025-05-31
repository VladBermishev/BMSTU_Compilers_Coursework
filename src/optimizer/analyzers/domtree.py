from collections import defaultdict

import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.optimizer.analyzers.cfgnode import CFGNode


class DomTree:

    @staticmethod
    def domset(function: hir_values.Function):
        cfg_nodes = CFGNode.build_nodes(function)
        domset = {}
        all = set(function.blocks)
        for block in function.blocks:
            domset[block] = all
        domset[function.blocks[0]] = {function.blocks[0]}
        modified = True
        while modified:
            modified = False
            for block in function.blocks:
                temp = set()
                if len(cfg_nodes[block].parents) > 0:
                    temp = all
                    for pred in cfg_nodes[block].parents:
                        temp = temp & domset[pred]
                temp.add(block)
                if temp != domset[block]:
                    domset[block] = temp
                    modified = True
        return domset


    @staticmethod
    def dom(function: hir_values.Function):
        """Compute the dominator tree for a single function."""
        dom_nodes = {}
        dom_set = DomTree.domset(function)
        for block in function.blocks:
            dom_nodes[block] = set()
        for block, domset in dom_set.items():
            ds = domset - {block}
            if len(ds) == 0:
                continue
            elif len(ds) == 1:
                dom_nodes[next(iter(ds))].add(block)
            else:
                closest = next(iter(ds))
                for bk in ds:
                    if closest != bk and closest in dom_set[bk]:
                        closest = bk
                dom_nodes[closest].add(block)

        return dom_nodes

    @staticmethod
    def dom_front(function: hir_values.Function):
        """Compute the dominator frontier for a single function."""
        dom = DomTree.dom(function)
        idom = {}
        for block, nodes in dom.items():
            for node in nodes:
                idom[node] = block
        dom_front = defaultdict(set)
        cfg_nodes = CFGNode.build_nodes(function)
        for block in function.blocks:
            for pred in cfg_nodes[block].parents:
                current = pred
                while current != idom[block]:
                    dom_front[current].add(block)
                    if current == function.blocks[0]:
                        break
                    current = idom[current]
        return dom_front