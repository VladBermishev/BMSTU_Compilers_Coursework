from dataclasses import dataclass
from src.libs import parser_edsl as pe
from pathlib import Path

@dataclass
class FileInclude:
    pos: pe.Position
    filepath: str

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        include_kw, lbr, filepath, rbr = attrs
        cinclude_kw, clbr, cfilepath, crbr = coords
        return FileInclude(cinclude_kw, filepath)


@dataclass
class PragmaCommand:
    pos: pe.Position
    command: str

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        pragma_kw, command = attrs
        cpragma_kw, ctext = coords
        return PragmaCommand(cpragma_kw, command)

@dataclass
class Program:
    source_lines: list[str | FileInclude | PragmaCommand]

    @staticmethod
    @pe.ExAction
    def create(attrs, coords, res_coord):
        return Program(attrs)
