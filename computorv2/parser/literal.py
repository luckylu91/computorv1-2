from typing import Union, Dict
from math_types import Rational, Complex, Matrix
from tokenizing import Token, tokens_str
from errors import UnknownFunctionError
from evaluation_utils import new_sign

# Context = Dict[str, Union[Rational, Complex, expr.Expr]]


# literal: unit_literal | matrix | function
class Literal:
    NUMBER = "NUMBER"
    VARIABLE = "VARIABLE"
    MATRIX = "MATRIX"
    FUNCTION = "FUNCTION"

    def __init__(self, type: 'str', value): #, sign: 'str' = Token.PLUS):
        self.type = type
        # unit_literal -> value: Rational | Complex | str
        # function -> value: tuple[fname: str, arg: str | Rational | Complex | Matrix]
        # matrix -> value: 'Matrix'[Rational | Complex | str]
        self.value = value
        # self.sign = sign

    # def set_sign(self, sign: 'str'):
    #     self.sign = sign

    # def apply_sign(self, sign):
    #     print(sign)
    #     self.sign = new_sign(self.sign, sign)

    @classmethod
    def _substitute_function_arg(cl, arg: 'Literal', context):
        if arg.type in (Literal.NUMBER, Literal.MATRIX, Literal.VARIABLE):
            return arg.evaluate(context)
        raise Exception()

    # def _apply_sign(self, val):
    #     return val if self.sign == Token.PLUS else -val

    def evaluate(self, context):
        if self.type == Literal.NUMBER:
            res = self.value
        elif self.type == Literal.VARIABLE:
            res = context[self.value]
        elif self.type == Literal.FUNCTION:
            fun_name, arg = self.value
            if not fun_name in context:
                raise UnknownFunctionError(fun_name)
            fun_expr, variable_name = context[fun_name]
            arg_value = Literal._substitute_function_arg(arg, context)
            context_fun = {variable_name: arg_value}
            res = fun_expr.evaluate(context_fun)
        else:
            res = Matrix.elementwise_unary_operation(lambda x: x.evaluate(context), self.value)
        # return self._apply_sign(res)
        return res

    def replace(self, context):
        if self.type == Literal.NUMBER:
            return self.copy()
        elif self.type == Literal.VARIABLE:
            if self.value in context:
                return Literal(Literal.NUMBER, context[self.value])
            else:
                return self.copy()
        elif self.type == Literal.FUNCTION:
            fun_name, arg = self.value
            return Literal(Literal.FUNCTION, (fun_name, arg.replace(context)))

    def __str__(self) -> 'str':
        if self.type == Literal.MATRIX:
            s = str(self.value)
        elif self.type in (Literal.VARIABLE, Literal.NUMBER):
            s = f"({self.value}: {self.type})"
        else:
            s = f"{self.value[0]}{self.value[1]}"
        return s

    def __repr__(self) -> str:
        return self.__str__()


