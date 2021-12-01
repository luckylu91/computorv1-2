#!/usr/bin/env python3

from tokenizer import Token, Lexer, is_variable, is_number, tokenize, literal_to_rational
from math_types import Complex, Matrix
from typing import Union

def matmult(a, b):
    if not isinstance(a, Matrix) or not isinstance(b, Matrix):
        raise Exception()
    return Matrix.matmult(a, b)

def do_op(op, l1, l2):
    # print(f"Doing {l1} {op.value} {l2}")
    if op.type == Token.PLUS:
        return l1 + l2
    elif op.type == Token.MINUS:
        return l1 - l2
    elif op.type == Token.MULT:
        return l1 * l2
    elif op.type == Token.DIV:
        return l1 / l2
    elif op.type == Token.MOD:
        return l1 % l2
    elif op.type == Token.MATMULT:
        return matmult(l1, l2)

# without matrices
class Literal:
    NUMBER = "NUMBER"
    VARIABLE = "VARIABLE"
    MATRIX = "MATRIX"
    # FUNCTION_VARIABLE = "FUNCTION_VARIABLE"

    # context = {
    #     'i': Complex.i()
    # }

    def __init__(self, type, value):
        self.type = type
        self.value = value

        # if self.type == Literal.MATRIX:
        #     if len(set(len(line) for line in value)) > 1:
        #         raise Exception()

    def evaluate(self, context):
        if self.type == Literal.NUMBER:
            return literal_to_rational(self.value)
        elif self.type == Literal.VARIABLE:
            return context[self.value]
        else:
            return Matrix.elementwise_unary_operation(lambda x: x.evaluate(), self.value)

    def __str__(self):
        if self.type == Literal.MATRIX:
            s = str(self.value)
        else:
            s = f"({self.value}: {self.type})"
        return s


class Term:
    def __init__(self, factor):
        self.factor_first = factor
        self.factors = []
        self.operations = []

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


class Expr:
    def __init__(self, term):
        self.term_first = term
        self.terms = []
        self.operations = []

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

# """
# matl   : LBRACK INTEGER (COMA INTEGER)* RBRACK
# mat    : LBRACK matl (SEMICOL matl)* RBRACK
# literal: (INTEGER | mat | variable)
# factor : literal | LPAREN expr RPAREN
# term   : factor ((MATMULT | MULT | DIV | MOD) factor)*
# expr   : term ((PLUS | MINUS) term)*
# """

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = lexer.next_token()
        self.variables_present = set()

    def eat(self, token_type = None):
        tok = self.current_token
        if token_type == None or tok.type == token_type:
            self.current_token = self.lexer.next_token()
            return tok
        else:
            raise Exception()

    "matline: LBRACK unit_literal (COMA unit_literal)* RBRACK"
    def matline(self) -> list[Literal]:
        values = []
        self.eat(Token.LBRACK)
        values.append(self.eat(Token.LITERAL))
        while self.current_token.type == Token.COMA:
            self.eat()
            values.append(self._token_to_litteral(self.eat(Token.LITERAL)))
        self.eat(Token.RBRACK)
        return values

    "matfull: LBRACK matl (SEMICOL matl)* RBRACK"
    def matfull(self) -> list[list[Literal]]:
        lines = []
        self.eat(Token.LBRACK)
        lines.append(self.matline())
        while self.current_token.type == Token.SEMICOL:
            self.eat()
            lines.append(self.matline())
        self.eat(Token.RBRACK)
        return lines

    "Will produce a matfull for a matline or matfull"
    def matany(self) -> Matrix:
        tok1 = self.lexer.get_token(1)
        if tok1.type != Token.LBRACK:
            return Matrix([self.matline()])
        else:
            return Matrix(self.matfull())

    def _token_to_litteral(self, tok):
        if is_number(tok.value):
            type = Literal.NUMBER
        elif is_variable(tok.value):
            type = Literal.VARIABLE
            self.variables_present.add(tok.value)
        else:
            type = Literal.MATRIX
        return Literal(type, tok.value)

    "literal: unit_literal | matfull"
    def literal(self) -> Literal:
        tok = self.current_token
        if tok.type == Token.LITERAL:
            res = self._token_to_litteral(tok)
            self.eat()
            return res
        else:
            return Literal(Literal.MATRIX, self.matany())

    "factor: literal | LPAREN expr RPAREN"
    def factor(self) -> Union[Literal, Expr]:
        tok = self.current_token
        if tok.type == Token.LPAR:
            self.eat()
            res = self.expr()
            self.eat(Token.RPAR)
            return res
        else:
            return self.literal()

    "term: factor ((MATMULT | MULT | DIV | MOD) factor)*"
    def term(self) -> Term:
        t = Term(self.factor())
        while self.current_token.type in (Token.MULT, Token.DIV, Token.MOD, Token.MATMULT):
            op = self.eat()
            f = self.factor()
            t.push_back(op, f)
        return t

    "expr: term ((PLUS | MINUS) term)*"
    def expr(self) -> Expr:
        e = Expr(self.term())
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            op = self.eat()
            t = self.term()
            e.push_back(op, t)
        return e


if __name__ == '__main__':
    import sys

    if len(sys.argv) >= 2:
        line = sys.argv[1]
    else:
        line = "i * i"
    toks = tokenize(line)
    print("Tokens :\n", toks)
    lex = Lexer(toks)
    pars = Parser(lex)
    e = pars.expr()
    print("Parsed expression:\n", e)
    print(f"Variables present in expression :\n {{{', '.join(pars.variables_present)}}}")

    context = {
        'i': Complex.i()
    }
    print(e.evaluate(context))
