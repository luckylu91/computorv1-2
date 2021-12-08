# Generic Error class
class Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


# Syntax Errors
class SyntaxError(Error):
    def __init__(self, message: str) -> None:
        super().__init__("Syntax error: " + message)

class UnKnownTokenError(SyntaxError):
    def __init__(self, token_str: str) -> None:
        super().__init__(f"Unknown Token: {token_str}")

class UnexpectedTokenError(SyntaxError):
    def __init__(self, lexer, token) -> None:
        super().__init__(f"Unexpected Token: {token} (at position {lexer.pos})")

class WrongEqualSignCount(SyntaxError):
    def __init__(self, n_equals: int) -> None:
        super().__init__(f"Wrong number of equal sign in expression (must be 1, found {n_equals})")


# Logic Errors
class LogicError(Error):
    def __init__(self, message: str) -> None:
        super().__init__("Logic Error: " + message)

class UnknownVariablesError(LogicError):
    def __init__(self, unknown_variables: set) -> None:
        super().__init__(f"Unknown variables: {unknown_variables}")

class UnknownFunctionError(LogicError):
    def __init__(self, unknown_function: str) -> None:
        super().__init__(f"Unknown function: {unknown_function}")

class MatrixInMatrixError(LogicError):
    def __init__(self) -> None:
        super().__init__("You can't put a Matrix in a Matrix "\
            "(and valid matrix dimensions are 1 and 2)")

class RecursiveFunctionDefinitonError(LogicError):
     def __init__(self) -> None:
         super().__init__("Recursive function definition")


# Math Errors
class MathError(Error):
    def __init__(self, message: str) -> None:
        super().__init__("Math error: " + message)

class IncompatibleMatrixShapeError(MathError):
    def __init__(self, m1, m2) -> None:
        message = f"The following matrices have incompatible shape "\
            f"for matrix multiplication :\n{m1}\nand\n{m2}"
        super().__init__(message)

class DifferentMatrixShapeError(MathError):
    def __init__(self, m1, m2, op_name: str) -> None:
        message = f"The following matrices have incompatible shape "\
            f"for matrix {op_name} :\n{m1}\nand\n{m2}\n"\
            f"Shapes should be identical but are "\
            f"{(m1.h, m1.w)} and {(m2.h, m2.w)}"
        super().__init__(message)

class MatrixDivisionOperatorError(MathError):
    def __init__(self, m1, m2) -> None:
        message = f"You can't use the division operator '/' "\
            f"between two matrices.\nSaid matrices are\n{m1}\nand\n{m2}"
        super().__init__(message)

class DivisionByZeroError(MathError):
    def __init__(self) -> None:
        super().__init__("Division by zero")

class ConversionError(MathError):
    def __init__(self, val, target_type) -> None:
        super().__init__(f"Cannot convert from {type(val)} to {target_type}")

class ModuloError(MathError):
    def __init__(self, type1, type2) -> None:
        super().__init__(f"Invalid types for modulo: {type1} and {type2}")

class InvalidMatMultUseError(MathError):
    def __init__(self, m1, m2) -> None:
        message = f"Trying to use matrix multiplication between "\
            f"'{type(m1).__name__}' and '{type(m2).__name__}'"
        super().__init__(message)

