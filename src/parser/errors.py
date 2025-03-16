import src.parser.parser_edsl as pe


class SemanticError(pe.Error):
    pass


class BinBadType(SemanticError):
    def __init__(self, pos, left, op, right):
        self.pos = pos
        self.left = left
        self.op = op
        self.right = right

    @property
    def message(self):
        return f'Несовместимые типы: {self.left} {self.op} {self.right}'


class UndefinedBinOperType(SemanticError):
    def __init__(self, pos, left, op, right):
        self.pos = pos
        self.left = left
        self.op = op
        self.right = right

    @property
    def message(self):
        return f'Неопределённая операция: {self.left} {self.op} {self.right}'


class UnaryBadType(SemanticError):
    def __init__(self, pos, expr_type, op):
        self.pos = pos
        self.expr_type = expr_type
        self.op = op

    @property
    def message(self):
        return f'Неопределённая унарная операция: {self.op} {self.expr_type}'


class ArrayNotIntIndexing(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Массив индексируется не целочисленным типом: {self.type}'


class ArrayIndexingDimensionMismatchError(SemanticError):
    def __init__(self, pos, expected_len, found_len):
        self.pos = pos
        self.expected_len = expected_len
        self.found_len = found_len

    @property
    def message(self):
        return f'Размерность массива меньше, чем список индексирования: {self.expected_len} < {self.found_len}'

class IfNotIntCondition(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Условие имеет тип {self.type} вместо целочисленного'


class WhileNotIntCondition(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Цикл имеет тип {self.type} вместо целочисленного'


class ArrayNotIntInit(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Ожидался целый тип, получен {self.type}'


class NotIntFor(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Ожидался целый тип, получен {self.type}'


class UnexpectedNextFor(SemanticError):
    def __init__(self, pos, true_index, false_index):
        self.pos = pos
        self.true_index = true_index
        self.false_index = false_index

    @property
    def message(self):
        return f'Ожидался счётчик: {self.true_index}, получен: {self.false_index}'


class RedefinitionError(SemanticError):
    def __init__(self, pos, name, prev_def):
        self.pos = pos
        self.name = name
        self.prev_def = prev_def

    @property
    def message(self):
        return f'Повторное объявление символа {self.name}, объявленного ранее {self.prev_def}'


class UndefinedSymbol(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Символ {self.name} не определён'


class UndefinedFunction(SemanticError):
    def __init__(self, pos, name, type):
        self.pos = pos
        self.name = name
        self.type = type

    @property
    def message(self):
        return f'Функция {self.name}: {self.type} не определена'


class InappropriateExit(SemanticError):
    def __init__(self, pos, exit_stmt):
        self.pos = pos
        self.exit_stmt = exit_stmt

    @property
    def message(self):
        return f'Неопределённый exit: {self.exit_stmt}'


class InappropriateInitializerList(SemanticError):
    def __init__(self, pos, common_type, bad_type):
        self.pos = pos
        self.common_type = common_type
        self.bad_type = bad_type

    @property
    def message(self):
        return f'Список инициализаций не определён: ожидалось: {self.common_type}, встречено: {self.bad_type}'


class InitializerListDimensionMismatch(SemanticError):
    def __init__(self, pos, common_dims, found_dims):
        self.pos = pos
        self.common_dims = common_dims
        self.found_dims = found_dims

    @property
    def message(self):
        return f'Не совпадение размерностей списков инициализаций: ожидалось: {self.common_dims}, встречено: {self.found_dims}'


class ConversionError(SemanticError):
    def __init__(self, pos, from_type, to_type):
        self.pos = pos
        self.from_type = from_type
        self.to_type = to_type

    @property
    def message(self):
        return f'Невозможно преобразовать тип:{self.from_type} к типу:{self.to_type}'


class InitializationTypeError(SemanticError):
    def __init__(self, pos, var_type, expr_type):
        self.pos = pos
        self.var_type = var_type
        self.expr_type = expr_type

    @property
    def message(self):
        return f'Невозможно определить тип:{self.var_type} типом:{self.expr_type}'


class InitializationLengthMismatchError(SemanticError):
    def __init__(self, pos, expected_length, given_length):
        self.pos = pos
        self.expected_length = "[" + ','.join([str(length) for length in expected_length]) + "]"
        self.given_length = given_length

    @property
    def message(self):
        return f'Несоответствие размеров при инициализаций ожидалось:{self.expected_length} получено:{self.given_length}'


class InitializationUndefinedLengthError(SemanticError):
    def __init__(self, pos, undefined_length):
        self.pos = pos
        self.undefined_length = undefined_length

    @property
    def message(self):
        return f'Неопределённый размер при инициализаций:{self.undefined_length}'


class InitializationNonConstSize(SemanticError):
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

    @property
    def message(self):
        return f'Размер не является константным при инциализаций списком:{self.size}'


class InitializationNegativeSize(SemanticError):
    def __init__(self, pos, size):
        self.pos = pos
        self.size = size

    @property
    def message(self):
        return f'Размер не может являться отрицательным:{self.size}'


class MultipleVariadicArgumentsInProtoError(SemanticError):
    def __init__(self, pos):
        self.pos = pos

    @property
    def message(self):
        return f'Больше 1 объявления переменного аргумента в функций:{self.pos}'


class VariadicArgumentsInProtoNotLastError(SemanticError):
    def __init__(self, pos):
        self.pos = pos

    @property
    def message(self):
        return f"Объявлениe переменного аргумента в функций не является последним:{self.pos}"