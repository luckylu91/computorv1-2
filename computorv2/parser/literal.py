from __future__ import annotations
from typing import Union, Dict
from math_types import Rational, Complex, Matrix
import expr
from evaluation_utils import rational_from_str
from tokenizer import Token

Context = Dict[str, Union[Rational, Complex, expr.Expr]]
Value = Union[Rational, Complex, Matrix]

# literal: unit_literal | matfull | function
class Literal:
    NUMBER = "NUMBER"
    VARIABLE = "VARIABLE"
    MATRIX = "MATRIX"
    FUNCTION = "FUNCTION"

    def __init__(self, type, value, sign: str = Token.PLUS):
        self.type = type
        # unit_literal -> value: Rational | Complex | str
        # function -> value: tuple[fname: str, arg: str | Rational | Complex | Matrix]
        # matrix -> value: Matrix[Rational | Complex | str]
        self.value = value
        self.sign = sign

    def set_sign(self, sign):
        self.sign = sign

    @classmethod
    def _substitute_function_arg(cl, arg: Literal, context: Context) -> Value:
        if arg.type in (Literal.NUMBER, Literal.MATRIX, Literal.VARIABLE):
            return arg.evaluate(context)
        raise Exception()

    def _apply_sign(self, val):
        return val if self.sign == Token.PLUS else -val

    def evaluate(self, context: Context) -> Value:
        if self.type == Literal.NUMBER:
            res = rational_from_str(self.value)
        elif self.type == Literal.VARIABLE:
            res = context[self.value]
        elif self.type == Literal.FUNCTION:
            fun_name, arg = self.value
            if not fun_name in context:
                raise Exception()
            fun_expr, variable_name = context[fun_name]
            arg_value = Literal._substitute_function_arg(arg, context)
            context_fun = {variable_name: arg_value}
            res = fun_expr.evaluate(context_fun)
        else:
            res = Matrix.elementwise_unary_operation(lambda x: x.evaluate(context), self.value)
        return self._apply_sign(res)

    def __str__(self) -> str:
        if self.type == Literal.MATRIX:
            s = str(self.value)
        else:
            s = f"({'+' if self.sign == Token.PLUS else '-'}{self.value}: {self.type})"
        return s
