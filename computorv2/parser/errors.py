class Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class SyntaxError(Error):
    def __init__(self, message: str) -> None:
        super().__init__("Syntax error: " + message)

class UnexpectedTokenError(SyntaxError):
    def __init__(self, lexer, token) -> None:
        super().__init__(f"Unexpected Token: {token} (at position {lexer.pos})")

class MathError(Error):
    def __init__(self, message: str) -> None:
        super().__init__("Math error: " + message)

class IncompatibleMatrixShapeError(MathError):
    def __init__(self, m1, m2) -> None:
        message = f"The following matrices have incompatible shape "\
            f"for matrix multiplication :\n{m1}\nand\n{m2}"
        super().__init__(message)

class DivisionByZeroError(MathError):
    def __init__(self) -> None:
        super.__init__("Division by zero")

