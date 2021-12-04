class Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

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

class MatrixWrongMultiplicationOperatorError(MathError):
    def __init__(self, m1, m2) -> None:
        message = f"You can't use the multiplication operator '*' "\
            f"between two matrices.\nInstead use the matrix multiplication "\
            f"operator '**'.\nSaid matrices are\n{m1}\nand\n{m2}"
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


