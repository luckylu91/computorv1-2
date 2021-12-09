from typing import Union, List, Any, Callable
from copy import deepcopy
from functools import reduce

from .math_types import Matrix
from .poly import Poly
from ..parsing.tokenizing import Token, tokens_str
from ..utils.python_types import Factor, Value, Context
from ..utils.errors import UnknownFunctionError, InvalidMatMultUseError, \
                           NonPolynomialEquation

def matmult(m1: 'Matrix', m2: 'Matrix') -> Matrix:
    if not isinstance(m1, Matrix) or not isinstance(m2, Matrix):
        raise InvalidMatMultUseError(m1, m2)


def do_op(op: 'str', l1: 'Literal', l2: 'Literal') -> 'Value':
    # print(f"do_op({op}, {l1}: {type(l1).__name__}, {l2}: {type(l2).__name__})")
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    if op == Token.PLUS:
        return l1 + l2
    elif op == Token.MINUS:
        return l1 - l2
    elif op == Token.MULT:
        return l1 * l2
    elif op == Token.DIV:
        return l1 / l2
    elif op == Token.MOD:
        return l1 % l2
    elif op == Token.POW:
        return l1 ** l2
    elif op == Token.MATMULT:
        return matmult(l1, l2)


def new_sign(sign1: 'str', sign2: 'str'):
    if sign1 == sign2:
        return Token.PLUS
    else:
        return Token.MINUS

# literal: unit_literal | matrix | function
class Literal:
    NUMBER = "NUMBER"
    VARIABLE = "VARIABLE"
    MATRIX = "MATRIX"
    FUNCTION = "FUNCTION"
    FUN_VARIABLE = "FUN_VARIABLE"

    # unit_literal -> value: Rational | Complex | str
    # function -> value: tuple[fname: str, arg: str | Rational | Complex | Matrix]
    # matrix -> value: Matrix[Rational | Complex | str]
    def __init__(self, type: 'str', value: 'Any'): #, sign: 'str' = Token.PLUS):
        self.type = type
        self.value = value

    def evaluate(self, context: 'Context') -> 'Value':
        if self.type == Literal.NUMBER:
            return self.value
        elif self.type == Literal.VARIABLE:
            return context[self.value]
        elif self.type == Literal.FUNCTION:
            fun_name, arg = self.value
            if not fun_name in context:
                raise UnknownFunctionError(fun_name)
            if arg.type not in (Literal.NUMBER, Literal.MATRIX, Literal.VARIABLE):
                raise Exception()
            fun_expr, variable_str = context[fun_name]
            arg_value = arg.evaluate(context)
            context_fun = {variable_str: arg_value}
            return fun_expr.evaluate(context_fun)
        elif self.type == Literal.MATRIX:
            return Matrix.elementwise_unary_operation(lambda x: x.evaluate(context), self.value)
        elif self.type == Literal.FUN_VARIABLE:
            if not f"FUN_VAR[{self.value}]" in context:
                raise Exception()
            return context[f"FUN_VAR[{self.value}]"]

    def replace(self, context: 'Context') -> None:
        if self.type == Literal.VARIABLE and self.value in context:
            self.type = Literal.NUMBER
            self.value = context[self.value]
        elif self.type == Literal.FUNCTION:
            self.value[1].replace(context)

    def contains_variables(self) -> None:
        return self.type in (Literal.VARIABLE, Literal.FUN_VARIABLE)

    def fun_expanded(self, context: 'Context') -> 'Union[Expr, Literal]':
        if self.type == Literal.FUNCTION:
            fun_name, arg = self.value
            if not fun_name in context:
                raise UnknownFunctionError(fun_name)
            if arg.type not in (Literal.NUMBER, Literal.MATRIX, Literal.VARIABLE):
                raise Exception()
            fun_expr, _ = context[fun_name]
            return deepcopy(fun_expr)
        else:
            return deepcopy(self)


    def __str__(self) -> 'str':
        if self.type == Literal.MATRIX:
            s = str(self.value)
        elif self.type in (Literal.VARIABLE, Literal.NUMBER, Literal.FUN_VARIABLE):
            s = f"{self.value}->{self.type}"
        else:
            s = f"{self.value[0]}({self.value[1]})"
        return s

    def __repr__(self) -> 'str':
        return self.__str__()


# Term: Multiplication / Division / Modulo of Literals or Exprs (Factor)
# term: 'factor' ((MATMULT | MULT | DIV | MOD | POW) factor)*
class Term:

    def __init__(self, factor: 'Factor', sign: 'str' = Token.PLUS):
        self.factor_first: 'Factor' = factor
        self.factors: 'List[Factor]' = []
        self.operations: 'List[str]' = []
        self.sign: 'str' = sign

    def set_sign(self, sign: 'str') -> None:
        self.sign = sign

    def apply_sign(self, sign) -> None:
        if self.sign == sign:
            self.sign = Token.PLUS
        else:
            self.sign = Token.MINUS

    def push_back(self, op: 'str', factor: 'Factor') -> None:
        self.factors.append(factor)
        self.operations.append(op)

    def extend(self, op: 'str', other: 'Term') -> None:
        self.operations.extend([op, *other.operations])
        self.factors.extend([other.factor_first, *other.factors])

    def _apply_sign_to_result(self, val: 'Value') -> 'Value':
        return val if self.sign == Token.PLUS else -val

    def mapped_term(self, map_fun: 'Callable') -> 'Term':
        res = Term(map_fun(self.factor_first), self.sign)
        for op, factor in zip(self.operations, self.factors):
            res.push_back(op, map_fun(factor))
        return res

    def evaluate(self, context: 'Context') -> 'Value':
        scalar_term = self.mapped_term(lambda factor: factor.evaluate(context)) #
        f = lambda l1, l2: do_op(Token.POW, l1, l2) #
        scalar_term.do_one_operation(Token.POW, binary_fun=f) #
        # res = self.factor_first.evaluate(context)
        # fs = [f.evaluate(context) for f in self.factors]
        res = scalar_term.factor_first
        for op, f in zip(self.operations, scalar_term.factors):
            res = do_op(op, res, f)
        return self._apply_sign_to_result(res)

    def contains_variables(self) -> 'bool':
        for factor in [self.factor_first, *self.factors]:
            if isinstance(factor, Literal) and factor.type in (Literal.FUN_VARIABLE, Literal.VARIABLE):
                return True
            if isinstance(factor, Expr) and factor.contains_variables():
                return True
        return False

    def do_one_operation(self, op: 'str', binary_fun: 'Callable' = None) -> None:
        factors = [self.factor_first, *self.factors]
        operations = []
        i = 0
        i_op = 0
        while i_op < len(self.operations):
            while i_op < len(self.operations) and self.operations[i_op] == op:
                f1 = factors[i]
                f2 = factors[i + 1]
                factors[i] = binary_fun(f1, f2)
                factors.pop(i + 1)
                i_op += 1
            if i_op < len(self.operations):
                operations.append(self.operations[i_op])
            i += 1
            i_op += 1
        self.factor_first = factors[0]
        self.factors = factors[1:]
        self.operations = operations

    def do_modulos(self):
        def f(f1: 'Factor', f2: 'Factor'):
            if f1.contains_variables() or f2.contains_variables():
                raise NonPolynomialEquation()
            return Literal(Literal.NUMBER, f1.evaluate(set()) % f2.evaluate(set()))
        self.do_one_operation(Token.MOD, binary_fun=f)

    def is_polynomial(self):
        if not all(op in (Token.MULT, Token.DIV, Token.POW) for op in self.operations):
            return False
        op_factors = zip([Token.MULT, self.operations], [self.factor_first, *self.factors])
        for op, factor in op_factors:
            if isinstance(factor, Expr):
                if not factor.is_polynomial():
                    return False
            # TODO if variables simplifies to non-variable ?
            if op == Token.DIV and factor.contains_variables():
                return False
            if op == Token.POW and factor.contains_variables():
                return False
        return True

    @classmethod
    def _to_polynomial(cl, factor: 'Factor') -> 'Poly':
        if isinstance(factor, Literal):
            if factor.type == Literal.NUMBER:
                val = factor.value
                return Poly({0: val})
            else:
                return Poly.x()
        else:
            return factor.to_polynomial()

    def to_polynomial(self):
        poly_term = self.mapped_term(lambda factor: Term._to_polynomial(factor)) #
        f = lambda l1, l2: do_op(Token.POW, l1, l2) #
        poly_term.do_one_operation(Token.POW, binary_fun=f) #
        res = poly_term.factor_first
        for op, f in zip(self.operations, poly_term.factors):
            res = do_op(op, res, f)
        return self._apply_sign_to_result(res)
        # res = Poly.one()
        # for op, factor in zip([Token.MULT, *self.operations], [self.factor_first, *self.factors]):
        #     res = do_op(op, res, Term._to_polynomial(factor))
        # # op_factors = zip([Token.MULT, *self.operations], [self.factor_first, *self.factors])
        # # polys = [Term._to_polynomial(op, factor) for op, factor in op_factors]
        # # res = reduce(lambda x, y: x * y, polys, Poly.one())
        # return self._apply_sign_to_result(res)

    def _do_op(self, op, other: 'Union[Literal, Term]') -> 'Term':
        new_term = deepcopy(self)
        if isinstance(other, Literal):
            new_term.push_back(op, other)
        elif isinstance(other, Term):
            new_term.sign = new_sign(new_term.sign, other.sign)
            new_term.factors.extend([other.factor_first, *other.factors])
            new_term.operations.extend([op, *other.operations])
        else:
            raise Exception()
        return new_term

    def replace(self, context: Context):
        self.factor_first.replace(context)
        for factor in self.factors:
            factor.replace(context)

    def fun_expanded(self, context):
        res = Term(self.factor_first.fun_expanded(context), sign=self.sign)
        for op, factor in zip(self.operations, self.factors):
            res.push_back(op, factor.fun_expanded(context))
        return res

    def __str__(self):
        s = f"{tokens_str[self.sign]} {self.factor_first}"
        for op, f in zip(self.operations, self.factors):
            s += f" {tokens_str[op]} {f}"
        return s

    def __repr__(self) -> 'str':
        return self.__str__()


# Expr: Sum of Terms
# expr: 'term' ((PLUS | MINUS) term)*
class Expr:
    def __init__(self) -> None:
        self.terms: 'List[Term]' = []

    def apply_sign(self, sign):
        # distibutivity of sign over expression
        for t in self.terms:
            t.apply_sign(sign)

    def push_back(self, term):
        self.terms.append(term)

    def extend(self, other: 'Expr'):
        self.terms.extend(other.terms)

    def evaluate(self, context):
        res = None
        for t in self.terms:
            te = t.evaluate(context)
            res = do_op(Token.PLUS, res, te)
        return res

    def is_polynomial(self):
        return all(t.is_polynomial() for t in self.terms)

    def contains_variables(self):
        return any(t.contains_variables() for t in self.terms)

    def to_polynomial(self):
        polys = [t.to_polynomial() for t in self.terms]
        return reduce(lambda x, y: x + y, polys, Poly.zero())

    def replace(self, context):
        for term in self.terms:
            term.replace(context)

    def fun_expanded(self, context):
        res = Expr()
        for term in self.terms:
            res.push_back(term.fun_expanded(context))
        return res

    def do_modulos(self):
        for term in self.terms:
            term.do_modulos()


    # op in (Token.MULT, Token.DIV)
    # def _develop(self, op, other):
    #     if isinstance(other, Literal) or isinstance(other, Term):
    #         res_expr = Expr(self.term_first._develop(op, other))
    #         for expr_op, term in zip(self.operations, self.terms):
    #             res_expr.push_back(expr_op, term._develop(op))
    #         return res_expr
    #     elif isinstance(other, Expr):

    # def _do_op(self, op, other, reverse = False):
    #     if not reverse:
    #         _do_op_term_term = lambda t1, t2: t1._do_op(op, t2)
    #     else:
    #         _do_op_term_term = lambda t1, t2: t2._do_op(op, t1)
    #     res_expr = Expr()
    #     if isinstance(other, Term):
    #         for t in self.terms:
    #             res_expr.push_back(_do_op_term_term(t, other))
    #     else:
    #         for t1 in self.terms:
    #             for t2 in self.terms:
    #                 res_expr.push_back(_do_op_term_term(t1, t2))
    #     return res_expr

    # NB: MULT distribtes over MOD... (on both MOD operands and that's all)
    # So no developement when MOD is present for the moment
    # MOD should be even more precedent
    # def __mul__(self, other):
    #     return self._do_op(Token.MULT, other, reverse=False)

    # def __rmul__(self, other):
    #     return self._do_op(Token.MULT, other, reverse=True)

    # def __truediv__(self, other):
    #     return self._do_op(Token.DIV, other, reverse=False)

    # def __rtruediv__(self, other):
    #     return self._do_op(Token.DIV, other, reverse=True)

    def __str__(self):
        s = ' '.join(f"{t}" for t in self.terms)
        return f"EXPR({s})"

    def __repr__(self) -> str:
        return self.__str__()



