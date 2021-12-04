from typing import List
from evaluation_utils import do_op
from literal import Literal
from tokenizing import Token

# term: 'factor' ((MATMULT | MULT | DIV | MOD) factor)*
class Term:

    def __init__(self, factor: 'Literal', sign: 'str' = Token.PLUS):
        self.factor_first: 'Literal' = factor
        self.factors: 'List[Literal]' = []
        self.operations: 'List[Token]' = []
        self.sign: 'str' = sign

    def set_sign(self, sign):
        self.sign = sign

    def push_back(self, op, factor):
        self.factors.append(factor)
        self.operations.append(op)

    def evaluate(self, context):
        res = self.factor_first.evaluate(context)
        fs = [f.evaluate(context) for f in self.factors]
        for op, f in zip(self.operations, fs):
            res = do_op(op, res, f)
        return res

    def __str__(self):
        s = str(self.factor_first)
        for op, f in zip(self.operations, self.factors):
            s += f" {op.value} {f}"
        return s

    def __repr__(self) -> str:
        return self.__str__()
