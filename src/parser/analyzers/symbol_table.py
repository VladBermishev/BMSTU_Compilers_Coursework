import pathlib
from enum import Enum
from src.parser.errors import RedefinitionError
from src.libs.parser_edsl import Position
import src.parser.basic_types as basic_types

class STBlockType(Enum):
    Undefined = 0
    GlobalBlock = 1
    FunctionBlock = 2
    SubroutineBlock = 3
    IfThenBlock = 4
    IfElseBlock = 5
    ForLoopBlock = 6
    WhileLoopBlock = 7

class STLookupScope(Enum):
    Undefined = 0
    Local = 1
    Global = 2
    Conditional = 3

class Symbol:

    def __init__(self, symbol_name, symbol_type, symbol_loc: Position = Position(),
                 _path=None, declaration=False, metadata=None):
        self.name = symbol_name
        self.type = symbol_type
        self.loc = symbol_loc
        self.declaration = declaration
        self.metadata = metadata
        self._path = _path

    def _set_path(self, path: pathlib.Path):
        self._path = path

    def path(self):
        return self._path

    def __eq__(self, other):
        if not isinstance(other, Symbol):
            return False
        return self.name == other.name and self.type == other.type



def symbol_name_predicate(lhs: Symbol, rhs: Symbol):
    return lhs.name == rhs.name

def symbol_type_name_predicate(lhs: Symbol, rhs: Symbol):
    return lhs.name == rhs.name and lhs.type == rhs.type

def symbol_basic_name_predicate(lhs: Symbol, rhs: Symbol):
    def __extract_type(tp: basic_types.Type):
        match type(tp):
            case t if t is basic_types.ProcedureT:
                return __extract_type(tp.return_type)
            case t if t is basic_types.ArrayT:
                return __extract_type(tp.value_type)
            case t if t is basic_types.PointerT:
                return __extract_type(tp.type)
        return tp
    return lhs.name == rhs.name and __extract_type(lhs.type) == __extract_type(rhs.type)


class STLookupStrategy:

    def __init__(self, symbol: Symbol, scope=STLookupScope.Global, predicate=symbol_name_predicate):
        self.symbol = symbol
        self.scope = scope
        self.predicate = predicate

    def match(self, symbol_to_test: Symbol):
        return self.predicate(self.symbol, symbol_to_test)

class STLookupResult:

    def __init__(self, values: list = None):
        self.results = [] if values is None else values

    def first(self):
        if len(self.results) == 0:
            raise IndexError()
        return self.results[0]

    def last(self):
        if len(self.results) == 0:
            raise IndexError()
        return self.results[-1]

    def where(self, predicate):
        return STLookupResult(list(filter(predicate, self.results)))

    def append(self, value):
        self.results.append(value)

    def length(self):
        return len(self.results)

    def empty(self):
        return len(self.results) == 0

    def __bool__(self):
        return bool(self.results)

    def __iter__(self):
        for result in self.results:
            yield result


class SymbolTable:

    def __init__(self, parent=None, uuid:int=None, block_type: STBlockType = STBlockType.GlobalBlock):
        self.parent = parent
        self.path = SymbolTable._resolve_path(self.parent, uuid)
        self.symbols = []
        self.children = []
        self.block_type = block_type
        self.metadata = None

    def add(self, symbol: Symbol, _is_meta=False):
        lookup_local_result = self.qnl(STLookupStrategy(symbol, STLookupScope.Global))
        if not lookup_local_result.empty():
            raise RedefinitionError(symbol.loc, symbol.name, lookup_local_result.first().loc)
        symbol._set_path(self.path/str(len(self.symbols)))
        self.symbols.append(symbol)
        if _is_meta:
            self.metadata = symbol

    def new_table(self, block_type: STBlockType = STBlockType.Undefined):
        result = SymbolTable(self, len(self.children), block_type)
        self.children.append(result)
        return result


    """
        Qualified Name Lookup: search for exact match of identifier and type
    """
    def qnl(self, strategy: STLookupStrategy) -> STLookupResult:
        strategy.predicate = symbol_type_name_predicate
        return self._lookup(strategy)

    """
        Unqualified Name Lookup: search for exact match of identifier
    """
    def unql(self, strategy: STLookupStrategy) -> STLookupResult:
        strategy.predicate = symbol_name_predicate
        return self._lookup(strategy)

    """
        TBasic Name Lookup: search for exact match of tbasic-name = {ident, type}
    """
    def bnl(self, strategy: STLookupStrategy) -> STLookupResult:
        strategy.predicate = symbol_basic_name_predicate
        return self._lookup(strategy)

    def _lookup(self, strategy: STLookupStrategy) -> STLookupResult:
        result = STLookupResult()
        current_node = self
        while current_node is not None:
            for local_symbol in current_node.symbols:
                if strategy.match(local_symbol):
                    result.append(local_symbol)
            if strategy.scope == STLookupScope.Local:
                break
            current_node = current_node.parent
        return result

    """
        Block Lookup: search for exact block types in upstream path
    """
    def bl(self, block_type: STBlockType = STBlockType.GlobalBlock) -> STLookupResult:
        result = STLookupResult()
        current_node = self
        while current_node is not None:
            if current_node.block_type == block_type:
                result.append(current_node)
            current_node = current_node.parent
        return result

    @staticmethod
    def _resolve_path(node=None, uuid:int = None):
        if node is None or uuid is None:
            return pathlib.Path('/')
        return node.path/str(uuid)

    @staticmethod
    def _root(node):
        result = node
        while result.parent is not None:
            result = result.parent
        return result

    def __getitem__(self, item: pathlib.Path):
        root = SymbolTable._root(self)
        current_node = root
        for table_uuid in item.parts[:-1]:
            if not (0 <= int(table_uuid) < len(current_node.children)):
                raise KeyError(item)
            current_node = current_node.children[table_uuid]
        if len(current_node.children) > 0:
            if not (0 <= int(item.parts[-1]) < len(current_node.children)):
                raise KeyError(item)
            return current_node.children[int(item.parts[-1])]
        else:
            if not (0 <= int(item.parts[-1]) < len(current_node.symbols)):
                raise KeyError(item)
            return current_node.symbols[int(item.parts[-1])]

    def __setitem__(self, key: pathlib.Path, value):
        root = SymbolTable._root(self)
        current_node = root
        for table_uuid in key.parts[:-1]:
            if not (0 <= int(table_uuid) < len(current_node.children)):
                raise KeyError(key)
            current_node = current_node.children[table_uuid]
        if len(current_node.children) > 0:
            if not (0 <= int(key.parts[-1]) < len(current_node.children)):
                raise KeyError(key)
            current_node.children[int(key.parts[-1])] = value
        else:
            if not (0 <= int(key.parts[-1]) < len(current_node.symbols)):
                raise KeyError(key)
            current_node.symbols[int(key.parts[-1])] = value

    def __iter__(self):
        for symbol in self.symbols:
            yield symbol
        for block in self.children:
            for symbol in block:
                yield symbol