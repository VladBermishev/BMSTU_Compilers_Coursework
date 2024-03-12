from errors import RedefinitionError
from enum import Enum


class SymbolTableBlockType(Enum):
    Undefined = 0
    GlobalBlock = 1
    FunctionBlock = 2
    SubroutineBlock = 3
    IfThenBlock = 4
    IfElseBlock = 5
    ForLoopBlock = 6
    WhileLoopBlock = 7


class Symbol:

    def __init__(self, varname, Tp, external=False, assoc_obj: object = None):
        self.name = varname
        self.type = Tp
        self.external = external
        self.llvm_obj = assoc_obj

    def assoc(self, assoc_obj: object):
        self.llvm_obj = assoc_obj
        return self


class SymbolTableLLVMEntry:

    def __init__(self, module, builder=None, assoc_obj=None):
        self.module = module
        self.builder = builder
        self.obj = assoc_obj

    def builder(self, builder):
        if builder:
            self.builder = builder
        return self

    def assoc(self, assoc_obj):
        if assoc_obj:
            self.obj = assoc_obj
        return self


class SymbolTable:

    def __init__(self, parent=None,
                 block_type: SymbolTableBlockType = SymbolTableBlockType.Undefined,
                 block_obj: object = None,
                 llvm_entry: SymbolTableLLVMEntry = None):
        self.parent = parent
        self.table = []
        self.children = []
        self.block_type = block_type
        self.block_obj = block_obj
        self.llvm = llvm_entry

    def add(self, symbol: Symbol):
        lookup_local_result = self.lookup(symbol, local=True)
        if lookup_local_result:
            raise RedefinitionError(symbol.name.pos, symbol.name, lookup_local_result.name.pos)
        self.table.append(symbol)

    def lookup(self, symbol: Symbol, local=False, by_name=True, by_type=True, by_origin=True, accumulate=False) \
            -> list[Symbol] | Symbol | None:
        current = self
        lookup_result = []
        while current:
            for current_symbol in current.table:
                result = True
                if by_name:
                    result &= symbol.name == current_symbol.name
                if by_type:
                    result &= symbol.type == current_symbol.type
                if by_origin:
                    result &= symbol.external == current_symbol.external
                if result:
                    if accumulate:
                        lookup_result += [current_symbol]
                    else:
                        return current_symbol
            if local:
                if accumulate:
                    return None if len(lookup_result) == 0 else lookup_result
                else:
                    return None
            current = current.parent
        if accumulate:
            return None if len(lookup_result) == 0 else lookup_result
        else:
            return None

    def lookup_block(self, block_type: SymbolTableBlockType, accumulate: bool = False):
        current = self
        lookup_result = []
        while current:
            if current.block_type == block_type:
                if accumulate:
                    lookup_result += [current]
                else:
                    return current
            current = current.parent
        if accumulate:
            return None if len(lookup_result) == 0 else lookup_result
        else:
            return None

    def new_local(self,
                  block_type: SymbolTableBlockType = SymbolTableBlockType.Undefined,
                  block_obj: object = None,
                  llvm_entry: SymbolTableLLVMEntry = None):
        local = SymbolTable(self, block_type=block_type, block_obj=block_obj, llvm_entry=llvm_entry)
        self.children.append(local)
        return local

    def builder(self, builder):
        self.llvm.builder(builder)
        return self

    def assoc(self, assoc_obj: object):
        self.llvm.assoc(assoc_obj)
        return self

    def print(self, t=0, id=0):
        print("-"*20 + str(id+1) + "-"*20)
        prefix = "\t" * t
        for symbol in self.table:
            print(f"{prefix}{symbol.name} {symbol.type}", flush=True)

        for child in self.children:
            id += 1
            child.print(t+1, id)
