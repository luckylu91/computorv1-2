#! /usr/bin/env python3

from typing import List, Union
from evaluation_utils import do_op
from expr import *
from literal import Literal
from tokenizing import Token, tokenize, tokens_str
from copy import deepcopy

# term: 'factor' ((MATMULT | MULT | DIV | MOD) factor)*
class Term:

    def __init__(self, factor: 'Literal', sign: 'str' = Token.PLUS):
        self.factor_first: 'Literal' = factor
        self.factors: 'List[Literal]' = []
        self.operations: 'List[str]' = []
        self.sign: 'str' = sign

    def set_sign(self, sign):
        self.sign = sign

    # def apply_sign(self, sign):
    #     self.factor_first.apply_sign(sign)
    #     print(self.factor_first)

    def push_back(self, op: 'str', factor):
        self.factors.append(factor)
        self.operations.append(op)

    def extend(self, op: 'str', other: 'Term'):
        self.operations.extend([op, *other.operations])
        self.factors.extend([other.factor_first, *other.factors])

    def _apply_sign_to_result(self, val):
        return val if self.sign == Token.PLUS else -val

    def evaluate(self, context):
        res = self.factor_first.evaluate(context)
        fs = [f.evaluate(context) for f in self.factors]
        for op, f in zip(self.operations, fs):
            res = do_op(op.type, res, f)
        return self._apply_sign_to_result(res)

    # def develop(self):
    #     for factor in [self.factor_first, *self.factors]:
    #         if isinstance(factor, Expr):
    #             res_expr = Expr()

    # def _develop(self, op, other: 'Union[Literal, Term]') -> 'Term':
    #     new_term = deepcopy(self)
    #     if isinstance(other, Literal):
    #         new_term.push_back(op, other)
    #     elif isinstance(other, Term):
    #         new_term.extend(op, other)
    #     else:
    #         raise Exception()
    #     return new_term

    @classmethod
    def generate_all_terms(cl, expressions, factor_operations):
        if len(expressions) == 1:
            for t in expressions[0].terms:
                yield deepcopy(t)
        else:
            for t0 in expressions[0].terms:
                for t in Term.generate_all_terms(expressions[1:], factor_operations[1:]):
                    t0_copy = deepcopy(t0)
                    t0_copy.extend(factor_operations[0], t)
                    yield t0_copy

    # only for MULT... DIV is not commutative
    def develop(self):
        operations = [Token.MULT, *self.operations]
        factors = [self.factor_first, *self.factors]
        expressions = filter(lambda x: isinstance(x, Expr), factors)
        if len(expressions) == 0:
            return deepcopy(self)
        res_expr = Expr()
        for t in Term.generate_all_terms(expressions, [Token.MULT for _ in range(len(expressions) - 1)]):
            res_expr.push_back(t)
        literals = filter(lambda x: not isinstance(x, Expr), factors)
        if len(literals) > 0:
            expr_literals = Expr()
            t0 = Term(literals[0], sign=self.sign)
            for factor in literals:
                t0.push_back(Token.MULT, factor)
                #.....


    # def __mul__(self, other: 'Union[Literal, Term]') -> 'Term':
    #     return self._develop(Token.MULT, other)

    # def __div__(self, other: 'Union[Literal, Term]') -> 'Term':
    #     return self._develop(Token.DIV, other)

    # def __rmul__(self, other: 'Union[Literal, Term]') -> 'Term':
    #     return self * other

    # def __rdiv__(self, other: 'Union[Literal, Term]') -> 'Term':
    #     raise Exception()

    def replace(self, context):
        res = Term(self.factor_first.replace(context))
        for op, factor in zip(self.operations, self.factors):
            res.push_back(op, factor.replace(context))
        return res

    def __str__(self):
        if self.sign == Token.MINUS:
            s = "- "
        else:
            s = ""
        s += f"{self.factor_first}"
        for op, f in zip(self.operations, self.factors):
            s += f" {tokens_str[op]} {f}"
        return s

    def __repr__(self) -> str:
        return self.__str__()


if __name__ == '__main__':
    e1 = Expr()
    e1.push_back(Term(Literal(Literal.NUMBER, "1")))
    e1.push_back(Term(Literal(Literal.NUMBER, "2")))
    e2 = Expr()
    e2.push_back(Term(Literal(Literal.NUMBER, "3")))
    e2.push_back(Term(Literal(Literal.NUMBER, "4")))

    print(" | ".join(str(t) for t in Term.generate_all_terms([e1, e2], [Token.MULT])))
