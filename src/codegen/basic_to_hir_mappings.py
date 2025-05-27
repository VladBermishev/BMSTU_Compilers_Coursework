import src.parser.basic_ast as basic_ast
import src.parser.basic_types as basic_types
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
                array_type = BasicToHirTypesMapping.get(basic_type.value_type)
                for size in reversed(basic_type.size):
                    array_type = hir_types.ArrayType(array_type, size)
                return array_type
            case t if t is basic_ast.ProcedureT:
                arguments = map(BasicToHirTypesMapping.get, basic_type.arguments_type)
                return hir_types.FunctionType(BasicToHirTypesMapping.get(basic_type.return_type), arguments)
            case t if t is basic_ast.StringT:
                return hir_types.ArrayType(BasicToHirTypesMapping.get(basic_type.value_type), basic_type.size[0] + 1)
            case t if t is basic_ast.PointerT and type(basic_type.type) is basic_ast.ArrayT:
                dims = hir_types.ArrayType(hir_types.IntType(), len(basic_type.type.size))
                return hir_types.StructType((hir_types.PointerType(), dims))
        return BasicToHirTypesMapping._TP_MAP[type(basic_type)]()

    @staticmethod
    def argument_get(basic_type: basic_types.Type):
        match type(basic_type):
            case t if t is basic_ast.ArrayT:
                array_type = BasicToHirTypesMapping.argument_get(basic_type.value_type)
                for size in reversed(basic_type.size):
                    array_type = hir_types.ArrayType(array_type, size)
                return array_type
            case t if t is basic_ast.ProcedureT:
                arguments = map(BasicToHirTypesMapping.argument_get, basic_type.arguments_type)
                return hir_types.FunctionType(BasicToHirTypesMapping.argument_get(basic_type.return_type), arguments)
            case t if t is basic_ast.StringT:
                return hir_types.ArrayType(BasicToHirTypesMapping.argument_get(basic_type.value_type), basic_type.size[0])
            case t if t is basic_ast.PointerT and type(basic_type.type) is basic_ast.ArrayT:
                return hir_types.PointerType()
        return BasicToHirTypesMapping._TP_MAP[type(basic_type)]()

class BasicToHirNamesMapping:
    @staticmethod
    def get(ast_node):
        match type(ast_node):
            case t if t is basic_ast.Varname:
                return hir_types.mangle(ast_node.name, BasicToHirTypesMapping.get(ast_node.type))
        return ""