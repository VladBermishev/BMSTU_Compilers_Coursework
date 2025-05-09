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

class PragmaUnknownCommand(SemanticError):
    def __init__(self, pos, bad_command):
        self.pos = pos
        self.command = bad_command

    @property
    def message(self):
        return f'Unknown pragma compiler command: {self.command}'

class IncludeInvalidPath(SemanticError):
    def __init__(self, pos, bad_path, locations):
        self.pos = pos
        self.path = bad_path
        self.locations = locations

    @property
    def message(self):
        return f'Invalid include path: {self.path}\nLocations:\n\t{"\n\t".join(map(str, self.locations))}'