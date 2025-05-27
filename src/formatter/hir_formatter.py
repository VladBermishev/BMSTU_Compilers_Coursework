import sys
from src.formatter.tree import TreeFormatterNode, TreeFormatter
import src.hir.values as hir_values
import src.hir.module as hir_module

class HirTreeFormatter(TreeFormatter):
    TAB = "  "
    LIST_ELEM = ""
    LAST_ELEM = ""
    COLUMN_SEP = ""

    @staticmethod
    def print(node, file=sys.stdout):
        HirTreeFormatter.__print(HirFormatterNode.create(node), file=sys.stdout)

    @staticmethod
    def __print(node: TreeFormatterNode, file=sys.stdout, _prefix="", _title_suffix="", _body_suffix=""):
        title_prefix = _prefix + _title_suffix
        subnode_prefix = _prefix + _body_suffix
        file.write(title_prefix + node.title + "\n")
        for idx, subnode in enumerate(node):
            HirTreeFormatter.__print(subnode, file=file,
                                  _prefix=subnode_prefix,
                                  _title_suffix=HirTreeFormatter.LAST_ELEM if idx == len(node) - 1 else HirTreeFormatter.LIST_ELEM,
                                  _body_suffix=HirTreeFormatter.TAB if idx == len(node) - 1 else HirTreeFormatter.COLUMN_SEP)


class HirFormatterNode(TreeFormatterNode):
    def __init__(self, title=None, node=None):
        if title is not None:
            super().__init__(title)
        elif node is not None:
            super().__init__(str(node))

    def __len__(self):
        return 0

    def __iter__(self):
        if False:
            yield self

    @staticmethod
    def create(node):
        match type(node):
            case t if t is hir_module.Module:
                return ModuleFormatterNode(node)
            case t if t is hir_values.GlobalVariable:
                return GlobalVariableFormatterNode(node)
            case t if t is hir_values.Function:
                return FunctionFormatterNode(node)
        return None

class ModuleFormatterNode(HirFormatterNode):
    def __init__(self, node: hir_module.Module):
        super().__init__(title=f"\'ModuleID = {node.name}")
        self.node = node

    def __len__(self):
        return len(self.node.constructors) + len(self.node.globals)

    def __iter__(self):
        for global_var in self.node.globals:
            yield HirFormatterNode.create(global_var)
        for constructor in self.node.constructors:
            yield HirFormatterNode.create(constructor)

class GlobalVariableFormatterNode(HirFormatterNode):
    def __init__(self, node: hir_values.GlobalVariable):
        super().__init__(node=node)

class FunctionFormatterNode(HirFormatterNode):
    def __init__(self, node: hir_values.Function):
        super().__init__(node=node)