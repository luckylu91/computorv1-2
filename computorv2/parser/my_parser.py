#!/usr/bin/env python3

from typing import Union, List
from tokenizing import Token, Lexer, is_variable, is_number
from math_types import Complex, Matrix
from literal import Literal
from expr import Expr
from term import Term
from errors import UnexpectedTokenError, UnknownVariablesError, MatrixInMatrixError, Error
from python_types import Context
import readline

# """
# matl   : LBRACK INTEGER (COMA INTEGER)* RBRACK
# mat    : LBRACK matl (SEMICOL matl)* RBRACK
# literal: (INTEGER | mat | variable)
# factor : literal | LPAREN expr RPAREN
# term   : factor ((MATMULT | MULT | DIV | MOD) factor)*
# expr   : term ((PLUS | MINUS) term)*
# """
class Parser:

    def __init__(self, lexer: 'Lexer', context: 'Context' = dict(), function_variables: 'set[str]' = set()):
        self.lexer: Lexer = lexer
        self.current_token: Token = lexer.next_token()
        self.variables_present = set()
        self.context = context
        self.function_variables = function_variables


    def eat(self, token_type: 'str' = None) -> 'Token':
        tok = self.current_token
        if token_type == None or tok.type == token_type:
            self.current_token = self.lexer.next_token()
            return tok
        else:
            raise UnexpectedTokenError(self.lexer, tok)


    def _token_to_unit_litteral(self, tok: 'Token') -> 'Literal':
        if is_number(tok.value):
            type = Literal.NUMBER
        elif is_variable(tok.value):
            type = Literal.VARIABLE
            self.variables_present.add(tok.value)
        else:
            type = Literal.MATRIX
        return Literal(type, tok.value)


    # matline: LBRACK unit_literal (COMA unit_literal)* RBRACK
    def matline(self) -> 'List[Literal]':
        values = []
        self.eat(Token.LBRACK)
        values.append(self.expr(matrix_allowed=False))
        while self.current_token.type == Token.COMA:
            self.eat()
            values.append(self.expr(matrix_allowed=False))
        self.eat(Token.RBRACK)
        return values


    # matfull: LBRACK matl (SEMICOL matl)* RBRACK
    def matfull(self) -> 'List[List[Literal]]':
        lines = []
        self.eat(Token.LBRACK)
        lines.append(self.matline())
        while self.current_token.type == Token.SEMICOL:
            self.eat()
            lines.append(self.matline())
        self.eat(Token.RBRACK)
        return lines


    def unit_literal(self) -> 'Literal':
        return self._token_to_unit_litteral(self.eat(Token.LITERAL))


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
        arg = self._token_to_unit_litteral(self.eat(Token.LITERAL))
        self.eat(Token.RPAR)
        return Literal(Literal.FUNCTION, (fname, arg))


    def eat_optional_sign(self, can_be_signed: 'bool') -> 'str':
        if can_be_signed and self.current_token.type in (Token.PLUS, Token.MINUS):
            sign = self.eat().type
        else:
            sign = Token.PLUS
        return sign


    # (can be signed)    literal: (PLUS | MINUS)? (unit_literal | matfull | function)
    # (cannot be signed) literal: unit_literal | matfull | function
    def literal(self, matrix_allowed=True) -> 'Literal':
        tok = self.current_token
        if tok.type == Token.LITERAL:
            if self.lexer.get_token(1).type == Token.LPAR:
                return self.function()
            else:
                return self.unit_literal()
                # res = self._token_to_unit_litteral(tok)
                # self.eat()
                # return res
        elif matrix_allowed:
            return self.matrix()
        raise MatrixInMatrixError()


    # factor: literal | LPAREN expr RPAREN
    def factor(self, can_be_signed: 'bool' = False, matrix_allowed=True) -> Union['Literal', 'Expr']:
        sign = self.eat_optional_sign(can_be_signed)
        tok = self.current_token
        if tok.type == Token.LPAR:
            self.eat()
            res = self.expr(matrix_allowed=matrix_allowed)
            self.eat(Token.RPAR)
        else:
            res = self.literal(matrix_allowed=matrix_allowed)
        res.set_sign(sign)
        return res


    # term: factor ((MATMULT | MULT | DIV | MOD) factor)*
    def term(self, can_be_signed: 'bool' = False, matrix_allowed=True) -> 'Term':
        t = Term(self.factor(can_be_signed=can_be_signed, matrix_allowed=matrix_allowed))
        while self.current_token.type in (Token.MULT, Token.DIV, Token.MOD, Token.MATMULT):
            op = self.eat()
            f = self.factor(can_be_signed=False, matrix_allowed=matrix_allowed)
            t.push_back(op, f)
        return t


    # expr: term ((PLUS | MINUS) term)*
    def expr(self, matrix_allowed=True) -> 'Expr':
        e = Expr(self.term(can_be_signed=True, matrix_allowed=matrix_allowed))
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            op = self.eat()
            t = self.term(can_be_signed=False, matrix_allowed=matrix_allowed)
            e.push_back(op, t)
        return e


    def expect_eof(self):
        self.eat(Token.EOF)
        unknown_variables = set(
            vp for vp in self.variables_present
                if vp not in self.context and vp not in self.function_variables
        )
        if len(unknown_variables) > 0:
            raise UnknownVariablesError(unknown_variables)


if __name__ == '__main__':
    from interpreting import interpret
    context = {
        'i': Complex.i()
    }
    while True:
        line = input()
        try:
            interpret(line, context)
            context_str = {k: str(v).replace('\n', ';') for k, v in context.items()}
            print(f"context is now : {context_str}")
        except Error as e:
            print(e)

