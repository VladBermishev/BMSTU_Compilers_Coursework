import src.parser.basic_ast as basic_ast
from src.codegen.basic_to_hir_mappings import BasicToHirTypesMapping, BasicToHirNamesMapping
from src.parser.analyzers.is_breakable import is_breakable
from src.parser.analyzers.is_const_expr import is_const_expr
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import SymbolTable, STBlockType
from src.hir.builder import HirBuilder
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types


class HirTransform:
    @staticmethod
    def transform(ast_node, source_id="", _parent=None, _st=None):
        match type(ast_node):
            case t if t is basic_ast.Program:
                return HirTransformProgram.transform(ast_node, source_id=source_id)
            case t if t is basic_ast.FunctionDecl or t is basic_ast.SubroutineDecl:
                return HirTransformFunctionDecl.transform(_parent, ast_node, st=_st)
            case t if t is basic_ast.FunctionDef:
                return HirTransformFunctionDef.transform(_parent, ast_node, st=_st)
            case t if t is basic_ast.SubroutineDef:
                return HirTransformFunctionDef.transform(_parent, ast_node, st=_st, _return_value=False)
            case t if t is basic_ast.VariableDecl:
                return HirTransformVariableDecl.transform(_parent, ast_node, st=_st)
            case t if t is basic_ast.InitializerList:
                return HirTransformInitializerList.transform(_parent, ast_node, st=_st)
            case t if t is basic_ast.ConstExpr:
                return HirTransformConstExpr.transform(_parent, ast_node, st=_st)
        return None

    @staticmethod
    def build(builder, ast_node, _st=None):
        match type(ast_node):
            case t if t is basic_ast.VariableDecl:
                return HirTransformVariableDecl.build(builder, ast_node, st=_st)
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
    def transform(module: hir_module.Module, ast_node: basic_ast.FunctionDecl, st: SymbolTable):
        arg_names = [ BasicToHirNamesMapping.get(arg.name) for arg in ast_node.proto.args]
        result = hir_values.Function(module,
                                     BasicToHirTypesMapping.get(ast_node.proto.type),
                                     BasicToHirNamesMapping.get(ast_node.proto.name),
                                     arg_names=arg_names)
        st.add(SymbolFactory.create(ast_node, metadata=result))
        return result

class HirTransformFunctionDef:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.FunctionDef | basic_ast.SubroutineDef, st: SymbolTable, _return_value=True):
        func = HirTransformFunctionDecl.transform(module, ast_node, st=st)
        builder = HirBuilder(func.append_basic_block("entry"))
        if is_breakable(ast_node):
            func.append_basic_block("return")

        function_st = st.new_table(STBlockType.FunctionBlock if _return_value else STBlockType.SubroutineBlock)
        if _return_value:
            func_ret_variable = basic_ast.Variable(ast_node.proto.name.pos, ast_node.proto.name, ast_node.proto.type.return_type)
            _return_value = builder.alloca(BasicToHirTypesMapping.get(ast_node.proto.type.return_type),1, ast_node.proto.name)
            function_st.add(SymbolFactory.create(func_ret_variable, metadata=_return_value), _is_meta=True)

        for ast_arg, hir_arg in zip(ast_node.proto.args, func.args):
            _return_value = builder.alloca(hir_arg.type, 1, f"{hir_arg.name}.addr")
            builder.store(hir_arg, _return_value)
            function_st.add(SymbolFactory.create(ast_arg, metadata=_return_value))

        for statement in ast_node.body:
            HirTransform.build(builder, statement, function_st)

        if not func.last_block.is_terminated:
            builder = HirBuilder(func.last_block)
        else:
            builder = HirBuilder(func.append_basic_block("return"))
        _return_instr = builder.ret(_return_value) if _return_value else builder.ret_void()
        return func

class HirTransformVariableDecl:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.VariableDecl, st: SymbolTable):
        init_value = None
        if ast_node.init_value:
            init_value = HirTransform.transform(ast_node.init_value, _parent=module)
        variable = hir_values.GlobalVariable(module, BasicToHirTypesMapping.get(ast_node.variable.type), ast_node.variable.name.name, init_value)
        st.add(SymbolFactory.create(ast_node.variable, metadata=variable))
        return variable

    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.VariableDecl, st: SymbolTable):
        ptr = builder.alloca(BasicToHirTypesMapping.get(ast_node.variable.type), 1, BasicToHirNamesMapping.get(ast_node.variable.name))
        st.add(SymbolFactory.create(ast_node.variable, metadata=ptr))
        init_value = None
        if ast_node.init_value:
            init_value = HirTransform.build(builder, ast_node.init_value)
        builder.store(init_value, ptr)
        return ptr

class HirTransformInitializerList:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.InitializerList, st: SymbolTable):
        if is_const_expr(ast_node):
            values = [HirTransform.transform(value, _parent=module, _st=st) for value in ast_node.values]
            return hir_values.ConstantValue(BasicToHirTypesMapping.get(ast_node.type), values)
        raise NotImplementedError()

    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.InitializerList, st: SymbolTable):
        if is_const_expr(ast_node):
            init_list = HirTransform.transform(ast_node, _parent=builder.module, _st=st)
            init_list = hir_values.GlobalVariable(builder.module,
                                                  init_list.type,
                                                  f"__const.{builder.function.name}.{ast_node.variable.name.name}",
                                                  init_list)
            builder.module.add_global(init_list)
        else:
            init_list = builder.alloca(BasicToHirTypesMapping.get(ast_node.type),1, "kek")
            builder.gep()
            pass
        return init_list


class HirTransformConstExpr:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.ConstExpr, st: SymbolTable):
        return hir_values.ConstantValue(BasicToHirTypesMapping.get(ast_node.type), ast_node.value)