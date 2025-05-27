import src.parser.basic_ast as basic_ast
from src.codegen.basic_to_hir_mappings import BasicToHirTypesMapping, BasicToHirNamesMapping
from src.parser.analyzers.is_breakable import is_breakable
from src.parser.analyzers.is_const_expr import is_const_expr
from src.parser.analyzers.symbol_factory import SymbolFactory
from src.parser.analyzers.symbol_table import SymbolTable, STBlockType, STLookupStrategy, STLookupScope
from src.hir.builder import HirBuilder
from src.hir.utils import mditer
import src.hir.module as hir_module
import src.hir.values as hir_values
import src.hir.types as hir_types
import src.hir.instructions as hir_instructions
from src.parser.transforms.semantic_relax_transform import SRInitializerList


class HirTransform:
    zero = hir_values.ConstantValue(hir_types.IntType(), 0)
    one = hir_values.ConstantValue(hir_types.IntType(), 1)

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
    def build(builder, ast_node, _st=None, _store_ptr=None):
        match type(ast_node):
            case t if t is basic_ast.VariableDecl:
                return HirTransformVariableDecl.build(builder, ast_node, st=_st)
            case t if t is basic_ast.InitializerList:
                return HirTransformInitializerList.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.ConstExpr:
                return HirTransformConstExpr.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.Variable:
                return HirTransformVariable.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.Array:
                return HirTransformArray.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.ArrayReference:
                return HirTransformArrayReference.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.PrintCall:
                return HirTransformPrintCall.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.LenCall:
                return HirTransformLenCall.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.FuncCall:
                return HirTransformFuncCall.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.ArrayIndex:
                return HirTransformArrayIndex.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.IfElseStatement:
                return HirTransformIfElseStatement.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.WhileLoop:
                return HirTransformWhileLoop.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.ForLoop:
                return HirTransformForLoop.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.ExitFor:
                return HirTransformExitFor.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t in (basic_ast.ExitWhile, basic_ast.ExitFunction, basic_ast.ExitSubroutine):
                return HirTransformExit.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.AssignStatement:
                return HirTransformAssignStatement.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.ImplicitTypeCast:
                return HirTransformImplicitTypeCast.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.UnaryOpExpr:
                return HirTransformUnaryOpExpr.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
            case t if t is basic_ast.BinOpExpr:
                return HirTransformBinOpExpr.build(builder, ast_node, st=_st, _store_ptr=_store_ptr)
        return None


class HirTransformProgram:
    @staticmethod
    def transform(ast_node: basic_ast.Program, source_id=""):
        module = hir_module.Module(source_id)
        symbol_table = SymbolTable(block_type=STBlockType.GlobalBlock)
        for decl in ast_node.decls:
            module.add_global(HirTransform.transform(decl, _parent=module, _st=symbol_table))
        return module

class HirTransformFunctionDecl:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.FunctionDecl, st: SymbolTable):
        arg_names = [ BasicToHirNamesMapping.get(arg.name) for arg in ast_node.proto.args]
        result = hir_values.Function(module,
                                     BasicToHirTypesMapping.argument_get(ast_node.proto.type),
                                     BasicToHirNamesMapping.get(ast_node.proto.name),
                                     arg_names=arg_names)
        st.add(SymbolFactory.create(ast_node, metadata=result))
        return result

class HirTransformFunctionDef:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.FunctionDef | basic_ast.SubroutineDef, st: SymbolTable, _return_value=True):
        func = HirTransformFunctionDecl.transform(module, ast_node, st=st)
        builder = HirBuilder(func.append_basic_block("entry"))
        bb_end = None
        if is_breakable(ast_node):
            bb_end = func.append_basic_block("return")

        function_st = st.new_table(STBlockType.FunctionBlock if _return_value else STBlockType.SubroutineBlock)
        if _return_value:
            func_ret_variable = basic_ast.Variable(ast_node.proto.name.pos, ast_node.proto.name, ast_node.proto.type.return_type)
            _return_value = builder.alloca(BasicToHirTypesMapping.get(ast_node.proto.type.return_type),1, ast_node.proto.name.name)
            function_st.add(SymbolFactory.create(func_ret_variable, metadata=_return_value))
            function_st.metadata = bb_end

        for ast_arg, hir_arg in zip(ast_node.proto.args, func.args):
            _hir_arg_ptr = builder.alloca(hir_arg.type, 1, f"{hir_arg.name}.addr")
            builder.store(hir_arg, _hir_arg_ptr)
            function_st.add(SymbolFactory.create(ast_arg, metadata=_hir_arg_ptr))

        for statement in ast_node.body:
            HirTransform.build(builder, statement, function_st)

        if not func.last_block.is_terminated:
            builder = HirBuilder(func.last_block)
            builder.position_at_end(func.last_block)
        else:
            bb_end = func.append_basic_block("return")
            builder.position_at_end(bb_end)
        _return_instr = builder.ret(_return_value) if _return_value else builder.ret_void()
        return func

class HirTransformVariableDecl:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.VariableDecl, st: SymbolTable):
        init_value = hir_values.HirDefaultValues.get(BasicToHirTypesMapping.get(ast_node.variable.type))
        if ast_node.init_value and is_const_expr(ast_node.init_value):
            init_value = HirTransform.transform(ast_node.init_value, _parent=module)
        variable = hir_values.GlobalVariable(module, BasicToHirTypesMapping.get(ast_node.variable.type), ast_node.variable.name.name, init_value)
        if ast_node.init_value and not is_const_expr(ast_node.init_value):
            ctor_tp = hir_types.FunctionType(hir_types.VoidType(), ())
            ctor = hir_values.Function(module, ctor_tp, f"__ctor.{ast_node.variable.name.name}", arg_names=())
            ctor_builder = HirBuilder(ctor.append_basic_block("entry"))
            HirTransform.build(ctor_builder, ast_node.init_value, st, _store_ptr=variable)
            ctor_builder.ret_void()
            module.add_constructor(ctor)
        st.add(SymbolFactory.create(ast_node.variable, metadata=variable))
        return variable

    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.VariableDecl, st: SymbolTable):
        ptr = builder.alloca(BasicToHirTypesMapping.get(ast_node.variable.type), 1, BasicToHirNamesMapping.get(ast_node.variable.name))
        st.add(SymbolFactory.create(ast_node.variable, metadata=ptr))
        return HirTransformVariableDecl.build_ptr_assignment(builder, ptr, ast_node.variable, ast_node.init_value, st)

    @staticmethod
    def build_ptr_assignment(builder: HirBuilder, ptr, ast_variable: basic_ast.Variable, ast_init: basic_ast.Expr, st: SymbolTable):
        tp = ptr.source_etype if isinstance(ptr, hir_instructions.GEPInstruction) else ptr.allocated_type
        init_value = hir_values.HirDefaultValues.get(tp)
        if ast_init:
            init_value = HirTransform.build(builder, ast_init, _store_ptr=ptr, _st=st)
        elif isinstance(ast_variable.type, basic_ast.ArrayT):
            init_value = hir_values.GlobalVariable(builder.module,
                                                   init_value.type,
                                                   f"__const.{builder.function.name}.{ast_variable.name.name}",
                                                   init_value)
            builder.module.add_global(init_value)

        # Uncertain eq operator
        if isinstance(ast_variable.type, basic_ast.ArrayT):
            if ptr != init_value:
                builder.copy(ptr, init_value, hir_types.sizeof(tp))
        elif isinstance(ast_variable.type, basic_ast.StringT):
            strcpy = st.qnl(STLookupStrategy(SymbolFactory.string_copy(), STLookupScope.Global)).first().metadata
            string = builder.call(strcpy, [ptr, init_value], "strcopy")
            builder.store(string, ptr)
        else:
            builder.store(init_value, ptr)
        return ptr

class HirTransformInitializerList:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.InitializerList, st: SymbolTable):
        assert is_const_expr(ast_node)
        values = [HirTransform.transform(value, _parent=module, _st=st) for value in ast_node.values]
        return hir_values.ConstantValue(BasicToHirTypesMapping.get(ast_node.type), values)

    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.InitializerList, st: SymbolTable, _store_ptr):
        if is_const_expr(ast_node):
            init_list = HirTransform.transform(ast_node, _parent=builder.module, _st=st)
            init_list = hir_values.GlobalVariable(builder.module,
                                                  init_list.type,
                                                  f"__const.{builder.function.name}.{_store_ptr.name}",
                                                  init_list)
            init_list.global_constant = True
            init_list.deduplicate()
            builder.module.add_global(init_list)
        else:
            init_list = _store_ptr
            for idx in mditer(SRInitializerList.dimensions(ast_node)):
                val_tp = BasicToHirTypesMapping.get(ast_node.type.value_type)
                elem_ptr = builder.gep(val_tp, init_list, idx, name=f"arrayinit.element.{'.'.join(map(str, idx))}")
                builder.store(HirTransform.build(builder, ast_node.get(idx), st), elem_ptr)
        return init_list

class HirTransformVariable:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.Variable, st: SymbolTable, _store_ptr=None):
        result = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global))
        return builder.load(result.first().metadata, ast_node.name.name, BasicToHirTypesMapping.get(ast_node.type))

class HirTransformArray:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.Variable, st: SymbolTable, _store_ptr=None):
        raise NotImplementedError()

class HirTransformConstExpr:
    @staticmethod
    def transform(module: hir_module.Module, ast_node: basic_ast.ConstExpr, st: SymbolTable):
        return hir_values.ConstantValue(BasicToHirTypesMapping.get(ast_node.type), ast_node.value)

    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ConstExpr, st: SymbolTable, _store_ptr=None):
        if isinstance(ast_node.type, basic_ast.StringT):
            const_value = hir_values.ConstantValue(BasicToHirTypesMapping.get(ast_node.type), ast_node.value)
            global_var = hir_values.GlobalVariable(builder.module, const_value.type, f"__str", const_value)
            global_var.global_constant = True
            global_var.deduplicate()
            builder.module.add_global(global_var)
            return global_var
        return hir_values.ConstantValue(BasicToHirTypesMapping.get(ast_node.type), ast_node.value)


class HirTransformArrayReference:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ArrayReference, st: SymbolTable, _store_ptr=None):
        if not (lookup_result := st.qnl(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global))).empty():
            return lookup_result.first().metadata
        array = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node.dereference()), STLookupScope.Global)).first()
        size = [hir_values.ConstantValue(hir_types.IntType(), sz) for sz in array.type.size]
        struct_ptr = builder.alloca(BasicToHirTypesMapping.get(ast_node.type))
        array_ptr = builder.gep(struct_ptr.allocated_type, struct_ptr, [0, 0], name=f"{ast_node.name.name}.ptr")
        builder.store(array.metadata, array_ptr)
        for idx, sz in enumerate(size):
            size_ptr = builder.gep(struct_ptr.allocated_type.elements_types[1], array_ptr, [0, idx], name=f"{ast_node.name.name}.dim.{idx}")
            builder.store(sz, size_ptr)
        return struct_ptr


class HirTransformPrintCall:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.PrintCall, st: SymbolTable, _store_ptr=None):
        args = [HirTransform.build(builder, arg, st) for arg in ast_node.args]
        prints = SymbolFactory.create(ast_node)
        for hir_arg, ast_arg, print_symbol in zip(args, ast_node.args, prints):
            print_func = st.qnl(STLookupStrategy(print_symbol, STLookupScope.Global)).first().metadata
            builder.call(print_func, [hir_arg])

class HirTransformLenCall:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.LenCall, st: SymbolTable, _store_ptr=None):
        match type(ast_node.array):
            case t if t is basic_ast.ImplicitTypeCast:
                return HirTransformLenCall.build_const_string(builder, ast_node, st)
            case t if t is basic_ast.Variable:
                return HirTransformLenCall.build_strlen(builder, ast_node, st)
            case t if t is basic_ast.ArrayReference:
                return HirTransformLenCall.build_struct_load(builder, ast_node.array, st)
            case t if t is basic_ast.ArrayIndex:
                return HirTransformLenCall.build_array_index(builder, ast_node.array, st)
            case t if t is basic_ast.BinOpExpr:
                return HirTransformLenCall.build_string_concatenation(builder, ast_node, st)
        raise NotImplementedError()

    @staticmethod
    def build_const_string(builder: HirBuilder, ast_node: basic_ast.LenCall, st: SymbolTable):
        # 'abcd' -> ConstValue(4)
        return hir_values.ConstantValue(hir_types.IntType(), ast_node.array.type.type.size[0])

    @staticmethod
    def build_strlen(builder: HirBuilder, ast_node: basic_ast.LenCall, st: SymbolTable):
        # str$ -> StringLength%(str$)
        strlen = st.qnl(STLookupStrategy(SymbolFactory.string_length(), STLookupScope.Global)).first().metadata
        string = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node.array), STLookupScope.Global)).first().metadata
        return builder.call(strlen, [string], "strlen.call")

    @staticmethod
    def build_struct_load(builder: HirBuilder, ast_node: basic_ast.ArrayReference, st: SymbolTable):
        # items$() -> items.dims[0]
        if not ast_node.is_size_undefined():
            symbol = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node.dereference()), STLookupScope.Global)).first()
            return hir_values.ConstantValue(hir_types.IntType(), symbol.type.size[0])
        array = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global)).first().metadata
        size_ptr = builder.gep(BasicToHirTypesMapping.get(ast_node.type), array, [0, 1, 0],
                               name=f"{ast_node.name.name}.len.ptr")
        return builder.load(size_ptr, name=f"{ast_node.name.name}.len.ptr", typ=hir_types.IntType())

    @staticmethod
    def build_array_index(builder: HirBuilder, ast_node: basic_ast.ArrayIndex, st: SymbolTable):
        if not ast_node.is_size_undefined():
            array = st.unql(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global)).first()
            return hir_values.ConstantValue(hir_types.IntType(), array.type.size[len(ast_node.args)])
        if isinstance(ast_node.type.type, basic_ast.StringT):
            string = HirTransform.build(builder, ast_node, st)
            strlen = st.qnl(STLookupStrategy(SymbolFactory.string_length(), STLookupScope.Global)).first().metadata
            return builder.call(strlen, [string])
        array = st.unql(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global)).first().metadata
        size_ptr = builder.gep(BasicToHirTypesMapping.get(ast_node.type), array, [0, 1, len(ast_node.args)], name=f"{ast_node.name.name}.len.ptr")
        return builder.load(size_ptr, name=f"{ast_node.name.name}.len.ptr", typ=hir_types.IntType())

    @staticmethod
    def build_string_concatenation(builder: HirBuilder, ast_node: basic_ast.LenCall, st: SymbolTable):
        # "abcd" + sep$ -> 4 + StringLength%(sep$)
        # "abcd" + "efgh" -> 8
        left = HirTransformLenCall.build(builder, basic_ast.LenCall(None, ast_node.array.left, basic_ast.IntegerT()), st)
        right = HirTransformLenCall.build(builder, basic_ast.LenCall(None, ast_node.array.right, basic_ast.IntegerT()), st)
        if isinstance(left, hir_values.ConstantValue) and isinstance(right, hir_values.ConstantValue):
            return hir_values.ConstantValue(hir_types.IntType(), left.value + right.value)
        return builder.add(left, right, "str.concat.len")

class HirTransformFuncCall:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.FuncCall, st: SymbolTable, _store_ptr=None):
        args = [HirTransform.build(builder, arg, st) for arg in ast_node.args]
        func = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global)).first().metadata
        return builder.call(func, args, name=f"call.{ast_node.name.name}")


class HirTransformArrayIndex:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ArrayIndex, st: SymbolTable, _store_ptr=None):
        value_ptr = HirTransformArrayIndex.build_ref(builder, ast_node, st)
        return builder.load(value_ptr, name=f"{ast_node.name.name}.val", typ=BasicToHirTypesMapping.get(ast_node.type))

    @staticmethod
    def build_ref(builder: HirBuilder, ast_node: basic_ast.ArrayIndex, st: SymbolTable, _store_ptr=None):
        indices = [HirTransform.build(builder, idx, st) for idx in ast_node.args]
        for i, idx in enumerate(indices):
            if isinstance(idx, hir_values.ConstantValue):
                indices[i] = hir_values.ConstantValue(hir_types.IntType(), idx.value - 1)
            else:
                indices[i] = builder.sub(idx, HirTransform.one, f"{ast_node.name.name}.index.{i}")
        array_symbol = st.unql(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global)).first()
        array = array_symbol.metadata
        array_ptr = builder.gep(array.type, array, [0, 0], name=f"{ast_node.name.name}.ptr")
        for i, idx in enumerate(indices[:-1]):
            array_ptr = builder.gep(hir_types.PointerType(), array_ptr, [indices[idx]], name=f"{ast_node.name.name}.idx")
            array_ptr = builder.load(array_ptr, name=f"{ast_node.name.name}.val.ptr", typ=hir_types.PointerType())
        return builder.gep(BasicToHirTypesMapping.get(ast_node.type), array_ptr, [indices[-1]], name=f"{ast_node.name.name}.idx")

class HirTransformIfElseStatement:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.IfElseStatement, st: SymbolTable, _store_ptr=None):
        bbend = builder.append_basic_block(name=f"endif")
        bbelse = None
        if ast_node.else_branch is not None and len(ast_node.else_branch) != 0:
            bbelse = builder.append_basic_block(name=f"if.else")
        bbif = builder.append_basic_block(name=f"if.then")
        builder.cbranch(HirTransform.build(builder, ast_node.condition, st), bbif, bbelse or bbend)
        st_then = st.new_table(STBlockType.IfThenBlock)
        st_then.metadata = bbend
        builder.position_at_end(bbif)
        for stmt in ast_node.then_branch:
            HirTransform.build(builder, stmt, st_then)
        if not builder.block.is_terminated:
            builder.branch(bbend)
        if bbelse is not None:
            st_else = st.new_table(STBlockType.IfElseBlock)
            st_else.metadata = bbend
            builder.position_at_end(bbelse)
            for stmt in ast_node.else_branch:
                HirTransform.build(builder, stmt, st_else)
            if not builder.block.is_terminated:
                builder.branch(bbend)
        builder.position_at_end(bbend)

class HirTransformWhileLoop:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.WhileLoop, st: SymbolTable, _store_ptr=None):
        if ast_node.type != basic_ast.WhileType.Endless:
            HirTransformWhileLoop.build_while(builder, ast_node, st)
        else:
            HirTransformWhileLoop.build_endless(builder, ast_node, st)

    @staticmethod
    def build_while(builder: HirBuilder, ast_node: basic_ast.WhileLoop, st: SymbolTable, _store_ptr=None):
        bbend = builder.append_basic_block(name=f"while.end")
        bbbody = builder.append_basic_block(name=f"while.body")
        bbcond = builder.append_basic_block(name=f"while.cond")
        builder.branch(bbcond if ast_node.type in (basic_ast.WhileType.PreWhile, basic_ast.WhileType.PreUntil) else bbbody)
        builder.position_at_end(bbcond)
        cond = HirTransform.build(builder, ast_node.condition, st)
        if ast_node.type in (basic_ast.WhileType.PreUntil, basic_ast.WhileType.PostUntil):
            cond = builder.xor(cond, hir_values.ConstantValue(hir_types.BoolType(), 1))
        builder.cbranch(cond, bbbody, bbend)
        st_body = st.new_table(STBlockType.WhileLoopBlock)
        st_body.metadata = bbend
        builder.position_at_end(bbbody)
        for stmt in ast_node.body:
            HirTransform.build(builder, stmt, st_body)
        if not builder.block.is_terminated:
            builder.branch(bbcond)
        builder.position_at_end(bbend)

    @staticmethod
    def build_endless(builder: HirBuilder, ast_node: basic_ast.WhileLoop, st: SymbolTable, _store_ptr=None):
        bbend = builder.append_basic_block(name=f"while.end")
        bbbody = builder.append_basic_block(name=f"while.body")
        builder.branch(bbbody)
        st_body = st.new_table(STBlockType.WhileLoopBlock)
        st_body.metadata = bbend
        builder.position_at_end(bbbody)
        for stmt in ast_node.body:
            HirTransform.build(builder, stmt, st_body)
        if not builder.block.is_terminated:
            builder.branch(bbbody)
        builder.position_at_end(bbend)

class HirTransformForLoop:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ForLoop, st: SymbolTable, _store_ptr=None):
        bbend = builder.append_basic_block(name=f"for.end")
        bbbody = builder.append_basic_block(name=f"for.body")
        bbinc = builder.append_basic_block(name=f"for.inc")
        bbcond = builder.append_basic_block(name=f"for.cond")
        idx_ptr = builder.alloca(BasicToHirTypesMapping.get(ast_node.variable.type), 1, BasicToHirNamesMapping.get(ast_node.variable.name))
        start = HirTransform.build(builder, ast_node.start, st, _store_ptr)
        builder.store(start, idx_ptr)
        builder.branch(bbcond)
        builder.position_at_end(bbcond)
        lhs = builder.load(idx_ptr,
                           name=f"{BasicToHirNamesMapping.get(ast_node.variable.name)}.cond",
                           typ=BasicToHirTypesMapping.get(ast_node.variable.type))
        rhs = HirTransform.build(builder, ast_node.end, st, _store_ptr)
        cond = builder.icmp_signed("<=", lhs, rhs, name=f"cmp")
        builder.cbranch(cond, bbbody, bbend)
        for_block = st.new_table(STBlockType.ForLoopBlock)
        for_block.add(SymbolFactory.create(ast_node.variable, metadata=idx_ptr), _is_meta=True)
        for_block.add(SymbolFactory.create(basic_ast.ExitFor(ast_node.variable.pos, ast_node.variable),metadata=bbend))
        builder.position_at_end(bbbody)
        for stmt in ast_node.body:
            HirTransform.build(builder, stmt, for_block)
        if not builder.block.is_terminated:
            builder.branch(bbinc)
        builder.position_at_end(bbinc)
        idx_to_inc = builder.load(idx_ptr,
                                  name=f"{BasicToHirNamesMapping.get(ast_node.variable.name)}.inc",
                                  typ=BasicToHirTypesMapping.get(ast_node.variable.type))
        incremented_idx = builder.add(idx_to_inc, HirTransform.one, name=f"inc")
        builder.store(incremented_idx, idx_ptr)
        builder.branch(bbcond)
        builder.position_at_end(bbend)

class HirTransformExitFor:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ExitFor, st: SymbolTable, _store_ptr=None):
        builder.branch(st.qnl(STLookupStrategy(SymbolFactory.create(ast_node), STLookupScope.Global)).first().metadata)

class HirTransformExit:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ExitStatement, st: SymbolTable, _store_ptr=None):
        block_type = None
        match type(ast_node):
            case t if t is basic_ast.ExitWhile:
                block_type = STBlockType.WhileLoopBlock
            case t if t is basic_ast.ExitFunction:
                block_type = STBlockType.FunctionBlock
            case t if t is basic_ast.ExitSubroutine:
                block_type = STBlockType.SubroutineBlock
        if block_type is None:
            raise TypeError(f"Unexpected type {type(ast_node)}")
        builder.branch(st.bl(block_type).first().metadata)

class HirTransformAssignStatement:
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.AssignStatement, st: SymbolTable, _store_ptr=None):
        ptr = None
        match type(ast_node.variable):
            case t if t is basic_ast.Variable:
                ptr = st.qnl(STLookupStrategy(SymbolFactory.create(ast_node.variable),STLookupScope.Global)).first().metadata
            case t if t is basic_ast.ArrayIndex:
                ptr = HirTransformArrayIndex.build_ref(builder, ast_node.variable, st)
        if ptr is None:
            raise TypeError(f"Unexpected type {type(ast_node.variable)}")
        return HirTransformVariableDecl.build_ptr_assignment(builder, ptr, ast_node.variable, ast_node.expr, st)

class HirTransformImplicitTypeCast:
    # Bool -> Int -zext> Long -sitofp> Float -fpext> Double
    # String -> ptr{String}
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.ImplicitTypeCast, st: SymbolTable, _store_ptr=None):
        if isinstance(ast_node.expr, basic_ast.ConstExpr) and isinstance(ast_node.expr.type, basic_ast.StringT):
            return HirTransform.build(builder, ast_node.expr, st)
        value = HirTransform.build(builder, ast_node.expr, st)
        cast = HirTransformImplicitTypeCast.__cast(BasicToHirTypesMapping.get(ast_node.expr.type),
                                                   BasicToHirTypesMapping.get(ast_node.type))
        return cast(builder, value, BasicToHirTypesMapping.get(ast_node.type), "conv")

    @staticmethod
    def __cast(value_type: hir_types.Type, target_type: hir_types.Type):
        match (value_type, target_type):
            case t if value_type.is_integral() and target_type.is_integral():
                return HirBuilder.zext
            case t if value_type.is_integral() and target_type.is_floating_point():
                return HirBuilder.sitofp
            case t if value_type.is_floating_point() and target_type.is_floating_point():
                return HirBuilder.fpext
        raise TypeError(f"Cannot cast {value_type} to {target_type}")

class HirTransformUnaryOpExpr:
    UNARY_OPERATORS = {
        #"not": lambda x: x.not_,
        #"+": lambda x: x.add,
        "-": lambda x: x.neg,
    }
    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.UnaryOpExpr, st: SymbolTable, _store_ptr=None):
        value = HirTransform.build(builder, ast_node.unary_expr, st, _store_ptr)
        if ast_node.op in HirTransformUnaryOpExpr.UNARY_OPERATORS:
            match value.type:
                case t if t.is_integral():
                    return builder.neg(value, name=f"sub")
                case t if t.is_floating_point():
                    return builder.fneg(value, name=f"sub")
        return value


class HirTransformBinOpExpr:
    COMPARISON_OPERATORS = {
        "<>": "!=",
        "=": "==",
        '<': '<',
        '>': '>',
        '<=': '<=',
        '>=': '>=',
    }
    ARITHMETIC_OPERATORS ={
        '+': (HirBuilder.add, HirBuilder.fadd),
        '-': (HirBuilder.sub, HirBuilder.fsub),
        '*': (HirBuilder.mul, HirBuilder.fmul),
        '/': (HirBuilder.sdiv, HirBuilder.fdiv)
    }
    ARITHMETIC_OPERATORS_NAMES = {
        '+': "add",
        '-': "sub",
        '*': "mul",
        '/': "div"
    }

    @staticmethod
    def build(builder: HirBuilder, ast_node: basic_ast.BinOpExpr, st: SymbolTable, _store_ptr=None):
        left = HirTransform.build(builder, ast_node.left, st, _store_ptr)
        right = HirTransform.build(builder, ast_node.right, st, _store_ptr)
        if ast_node.op in HirTransformBinOpExpr.COMPARISON_OPERATORS:
            operation = HirTransformBinOpExpr.COMPARISON_OPERATORS[ast_node.op]
            match (left.type, right.type):
                case (lt, rt) if lt.is_integral():
                    return builder.icmp_signed(operation, left, right, name=f"cmp")
                case (lt, rt) if lt.is_floating_point():
                    return builder.fcmp_ordered(operation, left, right, name=f"cmp")
        if ast_node.op in HirTransformBinOpExpr.ARITHMETIC_OPERATORS:
            func = None
            match (left.type, right.type):
                case (lt, rt) if BasicToHirTypesMapping.get(ast_node.type).is_integral():
                    func = HirTransformBinOpExpr.ARITHMETIC_OPERATORS[ast_node.op][0]
                case (lt, rt) if BasicToHirTypesMapping.get(ast_node.type).is_floating_point():
                    func = HirTransformBinOpExpr.ARITHMETIC_OPERATORS[ast_node.op][1]
            if func is not None:
                return func(builder, left, right, name=HirTransformBinOpExpr.ARITHMETIC_OPERATORS_NAMES[ast_node.op])
            if isinstance(ast_node.type, basic_ast.PointerT) and isinstance(ast_node.type.type, basic_ast.StringT):
                strcat = st.qnl(STLookupStrategy(SymbolFactory.string_concat(), STLookupScope.Global)).first().metadata
                return builder.call(strcat, [left, right], name=f"strcat")
        raise ValueError(f"Unsupported operator {ast_node.op}")
