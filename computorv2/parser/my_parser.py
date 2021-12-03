#!/usr/bin/env python3

from typing import Union

from tokenizer import Token, Lexer, is_variable, is_number
from math_types import Complex, Matrix
from literal import Literal
from expr import Expr
from term import Term

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
        self.lexer: Lexer = lexer
        self.current_token: Token = lexer.next_token()
        self.variables_present = set()

    def eat(self, token_type: str = None) -> 'Token':
        tok = self.current_token
        if token_type == None or tok.type == token_type:
            self.current_token = self.lexer.next_token()
            return tok
        else:
            raise Exception()

    def _token_to_litteral(self, tok: Token) -> 'Literal':
        if is_number(tok.value):
            type = Literal.NUMBER
        elif is_variable(tok.value):
            type = Literal.VARIABLE
            self.variables_present.add(tok.value)
        else:
            type = Literal.MATRIX
        return Literal(type, tok.value)

    # matline: LBRACK unit_literal (COMA unit_literal)* RBRACK
    def matline(self) -> 'list[Literal]':
        values = []
        self.eat(Token.LBRACK)
        values.append(self._token_to_litteral(self.eat(Token.LITERAL)))
        while self.current_token.type == Token.COMA:
            self.eat()
            values.append(self._token_to_litteral(self.eat(Token.LITERAL)))
        self.eat(Token.RBRACK)
        return values

    # matfull: LBRACK matl (SEMICOL matl)* RBRACK
    def matfull(self) -> 'list[list[Literal]]':
        lines = []
        self.eat(Token.LBRACK)
        lines.append(self.matline())
        while self.current_token.type == Token.SEMICOL:
            self.eat()
            lines.append(self.matline())
        self.eat(Token.RBRACK)
        return lines

    def unit_literal(self) -> 'Literal':
        return self._token_to_litteral(self.eat(Token.LITERAL))

    # def signed_unit_literal(self) -> 'Literal':


    # Will produce a matfull for a matline or matfull
    def matrix(self) -> 'Literal':
        tok1 = self.lexer.get_token(1)
        if tok1.type != Token.LBRACK:
            m = Matrix([self.matline()])
        else:
            m = Matrix(self.matfull())
        return Literal(Literal.MATRIX, m)

    def function(self) -> 'Literal':
        fname = self.eat(Token.LITERAL).value
        self.eat(Token.LPAR)
        arg = self._token_to_litteral(self.eat(Token.LITERAL))
        self.eat(Token.RPAR)
        return Literal(Literal.FUNCTION, (fname, arg))

    def eat_optional_sign(self, can_be_signed: bool) -> 'str':
        if can_be_signed and self.current_token.type in (Token.PLUS, Token.MINUS):
            sign = self.eat().type
        else:
            sign = Token.PLUS
        return sign

    # (can be signed)    literal: (PLUS | MINUS)? (unit_literal | matfull | function)
    # (cannot be signed) literal: unit_literal | matfull | function
    def literal(self) -> 'Literal':
        tok = self.current_token
        if tok.type == Token.LITERAL:
            if self.lexer.get_token(1).type == Token.LPAR:
                return self.function()
            else:
                return self.unit_literal()
                # res = self._token_to_litteral(tok)
                # self.eat()
                # return res
        else:
            return self.matrix()

    # factor: literal | LPAREN expr RPAREN
    def factor(self, can_be_signed: bool = False) -> 'Union[Literal, Expr]':
        sign = self.eat_optional_sign(can_be_signed)
        tok = self.current_token
        if tok.type == Token.LPAR:
            self.eat()
            res = self.expr()
            self.eat(Token.RPAR)
        else:
            res = self.literal()
        res.set_sign(sign)
        return res

    # term: factor ((MATMULT | MULT | DIV | MOD) factor)*
    def term(self, can_be_signed: bool = False) -> 'Term':
        t = Term(self.factor(can_be_signed=can_be_signed))
        while self.current_token.type in (Token.MULT, Token.DIV, Token.MOD, Token.MATMULT):
            op = self.eat()
            f = self.factor(can_be_signed=False)
            t.push_back(op, f)
        return t

    # expr: term ((PLUS | MINUS) term)*
    def expr(self) -> 'Expr':
        e = Expr(self.term(can_be_signed=True))
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            op = self.eat()
            t = self.term(can_be_signed=False)
            e.push_back(op, t)
        return e



if __name__ == '__main__':
    from interpret import interpret
    context = {
        'i': Complex.i()
    }
    while True:
        line = input()
        # try:
        interpret(line, context)
        context_str = {k: str(v).replace('\n', ';') for k, v in context.items()}
        print(f"context is now : {context_str}")
        # except Exception as e:
        #     print(e)

