import enum
from dataclasses import dataclass
from src.libs import parser_edsl as pe
from pathlib import Path

@dataclass
class FileInclude:
    pos: pe.Position
    filepath: str | Path

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        include_kw, filepath = attrs
        cinclude_kw, cspaces, clbr, cfilepath, crbr = coords
        return FileInclude(cinclude_kw, filepath)

class PragmaCommands(enum.Enum):
    ONCE = "once"

@dataclass
class PragmaCommand:
    pos: pe.Position
    command: str

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pragma_kw, command = attrs
        cpragma_kw, ctext = coords
        return PragmaCommand(cpragma_kw, command.strip())

@dataclass
class Program:
    source_lines: list[str | FileInclude | PragmaCommand]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        return Program(attrs[0])
