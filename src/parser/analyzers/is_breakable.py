import src.parser.basic_ast as basic_ast
from src.parser.analyzers.ast_dfs import BasicAstSearch
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import symbol_basic_name_predicate

def is_brace_sequence_balanced(seq, open_cond, close_cond):
    counter = 0
    for elem in seq:
        counter += 1 if open_cond(elem) else -1 if close_cond(elem) else 0
        if counter < 0:
            return False
    return counter == 0

# Currently can be used only after SRT
def is_breakable(ast_node):
    match type(ast_node):
        case t if t is basic_ast.FunctionDef:
            return BasicAstSearch.find(ast_node, lambda node: type(node) is basic_ast.ExitFunction) is not None
        case t if t is basic_ast.SubroutineDef:
            return BasicAstSearch.find(ast_node, lambda node: type(node) is basic_ast.ExitSubroutine) is not None
        case t if t is basic_ast.WhileLoop:
            def search_condition(node):
                if type(node) is basic_ast.WhileLoop:
                    return BasicAstSearch.find(node, lambda n: type(n) is basic_ast.ExitWhile) is not None
                return type(node) is basic_ast.ExitWhile
            bbs = BasicAstSearch.find_all(ast_node, search_condition)
            return is_brace_sequence_balanced(bbs, lambda n: type(n) is basic_ast.WhileLoop, lambda n: type(n) is basic_ast.ExitWhile)
        case t if t is basic_ast.ForLoop:
            def search_condition(node):
                if type(node) is basic_ast.ExitFor:
                    lhs, rhs = SymbolFactory.create(node.name), SymbolFactory.create(ast_node.variable)
                    return symbol_basic_name_predicate(lhs, rhs)
                return False
            return BasicAstSearch.find(ast_node, search_condition) is not None
    return False