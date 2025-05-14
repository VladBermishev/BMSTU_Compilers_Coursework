import sys
from abc import abstractmethod, ABC


class TreeFormatterNode(ABC):
    def __init__(self, title=""):
        self.title = title

    @abstractmethod
    def __len__(self):
        return 0

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError()

class TreeFormatter:
    TAB = "  "
    LIST_ELEM = "|-"
    LAST_ELEM = "`-"
    COLUMN_SEP = "| "

    @staticmethod
    def print(node: TreeFormatterNode, file=sys.stdout):
        TreeFormatter.__print(node, file)

    @staticmethod
    def __print(node: TreeFormatterNode, file=sys.stdout, _prefix="", _title_suffix="", _body_suffix=""):
        title_prefix = _prefix + _title_suffix
        subnode_prefix = _prefix + _body_suffix
        file.write(title_prefix + node.title + "\n")
        for idx, subnode in enumerate(node):
            TreeFormatter.__print(subnode, file=file,
                                  _prefix=subnode_prefix,
                                  _title_suffix=(TreeFormatter.LAST_ELEM if idx == len(node) - 1 else TreeFormatter.LIST_ELEM),
                                  _body_suffix=(TreeFormatter.TAB if idx == len(node) - 1 else TreeFormatter.COLUMN_SEP))

if __name__ == "__main__":
    class TestTreeFormatterNode(TreeFormatterNode):
        def __init__(self, obj: int | list):
            super().__init__(str(obj) if isinstance(obj, int) else "list")
            self.obj = obj

        def __len__(self):
            return 0 if isinstance(self.obj, int) else len(self.obj)

        def __iter__(self):
            if isinstance(self.obj, list):
                for elem in self.obj:
                    yield TestTreeFormatterNode(elem)

    data = [1, [10, [1, 1, 1], 10], [3, 4, 5]]
    data1 = [1, [1,1], [1]]
    TreeFormatter.print(TestTreeFormatterNode(data))