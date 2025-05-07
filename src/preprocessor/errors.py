import src.libs.parser_edsl as pe

class SemanticError(pe.Error):
    @property
    def message(self):
        raise NotImplementedError

class BinBadType(SemanticError):
    def __init__(self, pos, left, op, right):
        self.pos = pos
        self.left = left
        self.op = op
        self.right = right

    @property
    def message(self):
        return f'Несовместимые типы: {self.left} {self.op} {self.right}'