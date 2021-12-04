from typing import List
from evaluation_utils import do_op
from term import Term
from tokenizing import Token

# expr: 'term' ((PLUS | MINUS) term)*
class Expr:
    def __init__(self, term, sign: 'str' = Token.PLUS):
        self.term_first: 'Term' = term
        self.terms: 'List[Term]' = []
        self.operations: 'List[Token]' = []
        self.sign = sign

    def set_sign(self, sign):
        self.sign = sign

    def push_back(self, op, term):
        self.terms.append(term)
        self.operations.append(op)

    def evaluate(self, context):
        # distibutivity of sign over expression
        self.term_first.set_sign(self.sign)
        for t in self.terms:
            t.set_sign(self.sign)

        res = self.term_first.evaluate(context)
        ts = [t.evaluate(context) for t in self.terms]
        for op, t in zip(self.operations, ts):
            res = do_op(op, res, t)
        return res

    def __str__(self):
        s = str(self.term_first)
        for op, t in zip(self.operations, self.terms):
            s += f" {op.value} {t}"
        return f"({s})"

    def __repr__(self) -> str:
        return self.__str__()
