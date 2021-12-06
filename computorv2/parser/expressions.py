#!/usr/bin/env python3

from typing import Union, Dict, List
from math_types import Rational, Complex, Matrix
from tokenizing import Token, tokens_str
from evaluation_utils import do_op, new_sign
from python_types import Factor, Value, Context
from tokenizing import Token, tokens_str
from errors import UnknownFunctionError
from copy import deepcopy
from functools import reduce
from collections import defaultdict


# literal: unit_literal | matrix | function
class Literal:
    NUMBER = "NUMBER"
    VARIABLE = "VARIABLE"
    MATRIX = "MATRIX"
    FUNCTION = "FUNCTION"
    FUN_VARIABLE = "FUN_VARIABLE"

    def __init__(self, type: 'str', value): #, sign: 'str' = Token.PLUS):
        self.type = type
        # unit_literal -> value: Rational | Complex | str
        # function -> value: tuple[fname: str, arg: str | Rational | Complex | Matrix]
        # matrix -> value: 'Matrix'[Rational | Complex | str]
        self.value = value
        # self.sign = sign

    def evaluate(self, context):
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

    def replace(self, context):
        if self.type == Literal.VARIABLE and self.value in context:
            self.type = Literal.NUMBER
            self.value = context[self.value]
        elif self.type == Literal.FUNCTION:
            self.value[1].replace(context)

    def contains_variables(self):
        return self.type in (Literal.VARIABLE, Literal.FUN_VARIABLE)

    def fun_expanded(self, context):
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

    def __repr__(self) -> str:
        return self.__str__()


# Term: Multiplication / Division / Modulo of Literals or Exprs (Factor)
# term: 'factor' ((MATMULT | MULT | DIV | MOD) factor)*
class Term:

    def __init__(self, factor: 'Factor', sign: 'str' = Token.PLUS):
        self.factor_first: 'Factor' = factor
        self.factors: 'List[Factor]' = []
        self.operations: 'List[str]' = []
        self.sign: 'str' = sign

    def set_sign(self, sign):
        self.sign = sign

    def apply_sign(self, sign):
        if self.sign == sign:
            self.sign = Token.PLUS
        else:
            self.sign = Token.MINUS

    def push_back(self, op: 'str', factor: 'Factor'):
        self.factors.append(factor)
        self.operations.append(op)

    def extend(self, op: 'str', other: 'Term'):
        self.operations.extend([op, *other.operations])
        self.factors.extend([other.factor_first, *other.factors])

    def _apply_sign_to_result(self, val: 'Value'):
        return val if self.sign == Token.PLUS else -val

    def evaluate(self, context: 'Context'):
        res = self.factor_first.evaluate(context)
        fs = [f.evaluate(context) for f in self.factors]
        for op, f in zip(self.operations, fs):
            res = do_op(op, res, f)
        return self._apply_sign_to_result(res)

    def contains_variables(self):
        for factor in [self.factor_first, *self.factors]:
            if isinstance(factor, Literal) and factor.type in (Literal.FUN_VARIABLE, Literal.VARIABLE):
                return True
            if isinstance(factor, Expr) and factor.contains_variables():
                return True
        return False

    def do_modulos(self):
        factors = [self.factor_first, *self.factors]
        operations = []
        i = 0
        i_op = 0
        while i_op < len(self.operations):
            while i_op < len(self.operations) and self.operations[i_op] == Token.MOD:
                f1 = factors[i]
                f2 = factors[i + 1]
                if f1.contains_variables() or f2.contains_variables():
                    raise Exception()
                factors[i] = Literal(Literal.NUMBER, f1.evaluate(set()) % f2.evaluate(set()))
                factors.pop(i + 1)
                i_op += 1
            if i_op < len(self.operations):
                operations.append(self.operations[i_op])
            i += 1
            i_op += 1
        self.factor_first = factors[0]
        self.factors = factors[1:]
        self.operations = operations

    def is_polynomial(self):
        if not all(op in (Token.MULT, Token.DIV) for op in self.operations):
            return False
        op_factors = zip([Token.MULT, self.operations], [self.factor_first, *self.factors])
        for op, factor in op_factors:
            if isinstance(factor, Expr):
                if not factor.is_polynomial():
                    return False
            if op == Token.DIV and factor.contains_variables():
                return False
        return True

    @classmethod
    def _to_polynomial(cl, op: 'str', factor: 'Factor') -> 'Poly':
        if isinstance(factor, Literal):
            if factor.type == Literal.NUMBER:
                val = factor.value if op == Token.MULT else 1 / factor.value
                return Poly({0: val})
            else:
                assert(factor.type in (Literal.FUN_VARIABLE, Literal.VARIABLE))
                assert(op == Token.MULT)
                return Poly.x()
        else:
            return factor.to_polynomial()


    def to_polynomial(self):
        op_factors = zip([Token.MULT, *self.operations], [self.factor_first, *self.factors])
        polys = [Term._to_polynomial(op, factor) for op, factor in op_factors]
        res = reduce(lambda x, y: x * y, polys, Poly.one())
        return self._apply_sign_to_result(res)

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
        res = Term(self.factor_first.fun_expanded(context))
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


# TO POLY HANDLE MOD
# Expr: Sum of Terms
# expr: 'term' ((PLUS | MINUS) term)*
class Expr:
    # def __init__(self, term): #, sign: 'str' = Token.PLUS):
    #     self.term_first: 'Term' = term
    #     self.terms: 'List[Term]' = []
    #     self.operations: 'List[Token]' = []
    #     # self.sign = sign

    def __init__(self) -> None:
        self.terms: 'List[Term]' = []

    # def apply_sign(self, sign):
    #     # distibutivity of sign over expression
    #     self.term_first.apply_sign(sign)
    #     for t in self.terms:
    #         t.apply_sign(sign)

    def apply_sign(self, sign):
        # distibutivity of sign over expression
        for t in self.terms:
            t.apply_sign(sign)

    # def push_back(self, op, term):
    #     self.terms.append(term)
    #     self.operations.append(op)

    def push_back(self, term):
        self.terms.append(term)

    def extend(self, other: 'Expr'):
        self.terms.extend(other.terms)

    # def evaluate(self, context):
    #     # distibutivity of sign over expression
    #     res = self.term_first.evaluate(context)
    #     ts = [t.evaluate(context) for t in self.terms]
    #     for op, t in zip(self.operations, ts):
    #         res = do_op(op.type, res, t)
    #     return res

    def evaluate(self, context):
        # distibutivity of sign over expression
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

    def _do_op(self, op, other, reverse = False):
        if not reverse:
            _do_op_term_term = lambda t1, t2: t1._do_op(op, t2)
        else:
            _do_op_term_term = lambda t1, t2: t2._do_op(op, t1)
        res_expr = Expr()
        if isinstance(other, Term):
            for t in self.terms:
                res_expr.push_back(_do_op_term_term(t, other))
        else:
            for t1 in self.terms:
                for t2 in self.terms:
                    res_expr.push_back(_do_op_term_term(t1, t2))
        return res_expr

    # NB: MULT distribtes over MOD... (on both MOD operands and that's all)
    # So no developement when MOD is present for the moment
    # MOD should be even more precedent
    def __mul__(self, other):
        return self._do_op(Token.MULT, other, reverse=False)

    def __rmul__(self, other):
        return self._do_op(Token.MULT, other, reverse=True)

    def __truediv__(self, other):
        return self._do_op(Token.DIV, other, reverse=False)

    def __rtruediv__(self, other):
        return self._do_op(Token.DIV, other, reverse=True)


    # def __str__(self):
    #     s = str(self.term_first)
    #     for op, t in zip(self.operations, self.terms):
    #         s += f" {op.value} {t}"
    #     return f"({s})"

    def __str__(self):
        s = ' '.join(f"{t}" for t in self.terms)
        return f"EXPR({s})"

    def __repr__(self) -> str:
        return self.__str__()


class Poly:
    def __init__(self, d: 'Dict[int, Scalar]' = dict()) -> None:
        self.d = {i: v for i, v in d.items() if not (v == 0)}

    @classmethod
    def zero(cl):
        return Poly()

    @classmethod
    def one(cl):
        return Poly({0: 1})

    @classmethod
    def x(cl):
        return Poly({1: 1})

    def __add__(self, other: 'Poly') -> 'Poly':
        d = defaultdict(Rational.zero)
        for i, v in [*self.d.items(), *other.d.items()]:
            d[i] = d[i] + v
        return Poly(d)

    def __mul__(self, other: 'Poly') -> 'Poly':
        d = defaultdict(Rational.zero)
        for i, v1 in self.d.items():
            for j, v2 in other.d.items():
                d[i + j] = d[i + j] + v1 * v2
        return Poly(d)

    def __neg__(self):
        return Poly({i: -v for i, v in self.d.items()})

    def __str__(self):
        if len(self.d) == 0:
            return "0"
        strs = []
        for i, v in sorted(self.d.items(), key=lambda x: x[0], reverse=True):
            s = ""
            if i == 0 or v != 1:
                s += str(v)
            if i >= 1:
                if v != 1:
                    s += "*"
                s += "x"
                if i >=2:
                    s += "^" + str(i)
            strs.append(s)
        return ' + '.join(strs)





if __name__ == '__main__':
    e1 = Expr()
    # e1.push_back(Term(Literal(Literal.NUMBER, "1")))
    # e1.push_back(Term(Literal(Literal.NUMBER, "2")))
    # e2 = Expr()
    # e2.push_back(Term(Literal(Literal.NUMBER, "3")))
    # e2.push_back(Term(Literal(Literal.NUMBER, "4")))

    # print(" | ".join(str(t) for t in Term.generate_all_terms([e1, e2], [Token.MULT])))
    print(Poly.zero())
    print(Poly.one())
    print(Poly.x())
    print(Poly({0: 1, 1: 2, 2: 1}))

