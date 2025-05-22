import src.parser.basic_ast as basic_ast
import src.parser.basic_types as basic_types
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import SymbolTable
from src.hir.builder import HirBuilder
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types



class BasicToHirTypesMapping:
    _TP_MAP = {
        basic_types.Type: hir_types.Type,
        basic_types.VoidT: hir_types.VoidType,
        basic_types.BoolT: hir_types.BoolType,
        basic_types.CharT: hir_types.IntType,
        basic_types.IntegerT: hir_types.IntType,
        basic_types.LongT: hir_types.LongType,
        basic_types.FloatT: hir_types.FloatType,
        basic_types.DoubleT: hir_types.DoubleType,
        basic_types.PointerT: hir_types.PointerType,
        basic_types.ArrayT: hir_types.StructType,
        basic_types.ProcedureT: hir_types.FunctionType,
        basic_types.StringT: hir_types.ArrayType,
    }
    @staticmethod
    def get(basic_type: basic_types.Type):
        match type(basic_type):
            case t if t is basic_ast.ArrayT:
                dims = hir_types.ArrayType(BasicToHirTypesMapping.get(basic_type.size[0].type), len(basic_type.size))
                return hir_types.StructType((hir_types.PointerType(), dims))
            case t if t is basic_ast.ProcedureT:
                arguments = map(BasicToHirTypesMapping.get, basic_type.arguments_type)
                return hir_types.FunctionType(BasicToHirTypesMapping.get(basic_type.return_type), arguments)
            case t if t is basic_ast.StringT:
                return hir_types.ArrayType(BasicToHirTypesMapping.get(basic_type.value_type),basic_type.size[0])
        return BasicToHirTypesMapping._TP_MAP[basic_type]()

class BasicToHirNamesMapping:
    @staticmethod
    def get(ast_node):
        match type(ast_node):
            case t if t is basic_ast.Varname:
                return hir_types.mangle(ast_node.name, BasicToHirTypesMapping.get(ast_node.type))
        return ""

class HirTransform:
    @staticmethod
    def transform(ast_node, source_id="", _parent=None):
        match type(ast_node):
            case t if t is basic_ast.Program:
                return HirTransformProgram.transform(ast_node, source_id=source_id)
            case t if t is basic_ast.FunctionDecl or t is basic_ast.SubroutineDecl:
                return HirTransformFunctionDecl.transform(ast_node, module=_parent)
            case t if t is basic_ast.FunctionDef:
                return HirTransformFunctionDef.transform(ast_node, module=_parent)
            case t if t is basic_ast.SubroutineDef:
                return HirTransformFunctionDef.transform(ast_node, module=_parent, _return_value=False)
            case t if t is basic_ast.VariableDecl:
                return HirTransformVariableDecl.transform(ast_node, module=_parent)
        return None

    @staticmethod
    def build(ast_node, _builder=None):
        match type(ast_node):
            case t if t is basic_ast.Program:
                return HirTransformVariableDecl.build(ast_node, builder=_builder)
        return None


class HirTransformProgram:
    @staticmethod
    def transform(ast_node: basic_ast.Program, source_id=""):
        module = hir_module.Module(source_id)
        for decl in ast_node.decls:
            module.add_global(HirTransform.transform(decl, _parent=module))
        return module

class HirTransformFunctionDecl:
    @staticmethod
    def transform(ast_node: basic_ast.FunctionDecl, st: SymbolTable, module):
        symbol = SymbolFactory.create(ast_node)
        arg_names = [ BasicToHirNamesMapping.get(arg.name) for arg in ast_node.proto.args]
        result = hir_values.Function(module,
                                     BasicToHirTypesMapping.get(ast_node.proto.type),
                                     BasicToHirNamesMapping.get(ast_node.proto.name),
                                     arg_names=arg_names)
        st.add(symbol)
        return result

class HirTransformFunctionDef:
    @staticmethod
    def transform(ast_node: basic_ast.FunctionDef | basic_ast.SubroutineDef, module, _return_value=True):
        func_name = ""
        # ASSOC Symbol with this func
        return hir_values.Function(module, BasicToHirTypesMapping.get(ast_node.proto.type), func_name)

class HirTransformVariableDecl:
    @staticmethod
    def transform(ast_node: basic_ast.VariableDecl, module: hir_module.Module = None):
        init_value = None
        if ast_node.init_value:
            init_value = HirTransform.transform(ast_node.init_value, _parent=module)
        # ASSOC Symbol with this var
        return hir_values.GlobalVariable(module, BasicToHirTypesMapping.get(ast_node.variable.type), ast_node.variable.name.name, init_value)

    @staticmethod
    def build(ast_node: basic_ast.VariableDecl, builder: HirBuilder):
        var_name = ""
        # ASSOC Symbol with this ptr
        ptr = builder.alloca(BasicToHirTypesMapping.get(ast_node.variable.type), 1, var_name)
        init_value = None
        if ast_node.init_value:
            init_value = HirTransform.build(ast_node.init_value, _builder=builder)
        builder.store(init_value, ptr)
        return ptr