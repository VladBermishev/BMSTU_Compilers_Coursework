import src.parser.basic_ast as basic_ast
from src.hir.builder import HirBuilder
import src.hir.module as hir_module

class HirTransform:
    @staticmethod
    def transform(ast_node, source_id="", _parent=None):
        match type(ast_node):
            case t if t is basic_ast.Program:
                return HirTransformProgram.transform(ast_node, source_id=source_id)
        return None

class HirTransformProgram:
    @staticmethod
    def transform(ast_node: basic_ast.Program, source_id=""):
        module = hir_module.Module(source_id)
        for decl in ast_node.decls:
            module.add_global(HirTransform.transform(decl, _parent=module))
        return module