from enum import Enum
from dataclasses import dataclass
from ttoken import TokenType
from nodes import NodeType

class ErrorType(Enum):
    ExportError = -2
    InvalidFileNameError = -1

    InvalidCharacterError = 0           ### Lexer Error
    InvalidSyntaxError = 1              ### Parser Error

    ### Interpreter Errors

    InvalidStatementTypeError = 2
    DivisionByZeroError = 3
    InvalidConditionOperatorError = 4
    StringConcatenationError = 5
    VariableError = 6
    FunctionArgumentError = 7

class BaseError:
    def __init__(self, type: ErrorType, message: str = 'Base Unknown Error Case', line: int=1):
        raise Exception(f'{type.name} LINE {line}: {message}')

class InvalidCharacterError(BaseError):
    def __init__(self, character: str, line: int):
        message = f'Unexpected Character "{character}" appeared.'

        super().__init__(ErrorType.InvalidCharacterError, message, line)

class InvalidSyntaxError(BaseError):
    def __init__(self, tokenType: TokenType, line: int=1, extraMessage: str=''):
        message = f'Illegal Syntax Occured "{tokenType.name} : {tokenType.value}". {extraMessage}'

        super().__init__(ErrorType.InvalidSyntaxError, message, line)

class InvalidStatementTypeError(BaseError):
    def __init__(self, stmtType: NodeType, extraMessage: str='', line: int=1):
        message = f'Unwanted Statement Occured "{stmtType.name}". {extraMessage}'

        super().__init__(ErrorType.InvalidStatementTypeError, message, line)

class DivisionByZeroError(BaseError):
    def __init__(self, line: int=1):
        message = 'Cannot divide by 0, result undefined.'

        super().__init__(ErrorType.DivisionByZeroError, message, line)

class InvalidConditionOperatorError(BaseError):
    def __init__(self, tokenType: TokenType, line: int=1):
        message = f'Invalid Operator in Condition detected "{tokenType.name}".'

        super().__init__(ErrorType.InvalidConditionOperatorError, message, line)

class StringConcatenationError(BaseError):
    def __init__(self, line: int=1):
        message = 'You can only concatenate strings by using "+". Anyother operator is not available.'

        super().__init__(ErrorType.StringConcatenationError, message, line)

class VariableError(BaseError):
    def __init__(self, varName: str, line: int=1):
        message = f'Variable {varName} already exists.'

        super().__init__(ErrorType.VariableError, message, line)

class VariableUnexistentError(BaseError):
    def __init__(self, varName: str, line: int=1):
        message = f'Variable {varName} does not exist.'

        super().__init__(ErrorType.VariableError, message, line)

class FunctionArgumentError(BaseError):
    def __init__(self, numOfArguments, numOfParamaters, line: int=1):
        message = f'Number of Arguments {numOfArguments} does not match with number of paramaters {numOfParamaters}.'

        super().__init__(ErrorType.FunctionArgumentError, message, line)

class ExportError(BaseError):
    def __init__(self, exportType: NodeType, line: int = 1):
        message = f'Cannot export {exportType.name}. Only "Objects" are exportable.'

        super().__init__(ErrorType.ExportError, message, line)

class InvalidFileNameError(BaseError):
    def __init__(self, extension):
        message = f'Extension ".{extension}" is invalid, make sure to use ".rux" in order for it to work.'

        super().__init__(ErrorType.InvalidFileNameError, message, -1)
