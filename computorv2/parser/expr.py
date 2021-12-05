from typing import List
from evaluation_utils import do_op
from literal import Literal
from term import Term
from tokenizing import Token, tokens_str
from copy import deepcopy

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

    def extend(self, op: 'str', other: 'Expr'):
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

    def replace(self, context):
        res = Expr(self.term_first.replace(context))
        for op, term in zip(self.operations, self.terms):
            res.push_back(op, term.replace(context))
        return res

    # op in (Token.MULT, Token.DIV)
    # def _develop(self, op, other):
    #     if isinstance(other, Literal) or isinstance(other, Term):
    #         res_expr = Expr(self.term_first._develop(op, other))
    #         for expr_op, term in zip(self.operations, self.terms):
    #             res_expr.push_back(expr_op, term._develop(op))
    #         return res_expr
    #     elif isinstance(other, Expr):


    # NB: MULT distribtes over MOD... (on both MOD operands and that's all)
    # So no developement when MOD is present for the moment
    # MOD should be even more precedent
    # def __mul__(self, other):



    # def __str__(self):
    #     s = str(self.term_first)
    #     for op, t in zip(self.operations, self.terms):
    #         s += f" {op.value} {t}"
    #     return f"({s})"

    def __str__(self):
        s = ' '.join(str(t) for t in self.terms)
        return f"EXPR({s})"

    def __repr__(self) -> str:
        return self.__str__()
