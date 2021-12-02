from evaluation_utils import do_op
from term import Term
from tokenizer import Token

# expr: term ((PLUS | MINUS) term)*
class Expr:
    def __init__(self, term):
        self.term_first: Term = term
        self.terms: list[Term] = []
        self.operations: list[Token] = []

    def push_back(self, op, term):
        self.terms.append(term)
        self.operations.append(op)

    def evaluate(self, context):
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
