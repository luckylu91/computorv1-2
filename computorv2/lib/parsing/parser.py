from typing import Iterable, Union, List
from .tokenizing import Token, Lexer, is_variable, is_number
from ..blocks.expressions import Literal, Term, Expr
from ..blocks.math_types import Rational, Matrix
from ..utils.errors import UnexpectedTokenError, UnknownVariablesError, MatrixInMatrixError, RecursiveFunctionDefinitonError
from ..utils.python_types import Context


def rational_from_str(tok: 'str') -> 'Rational':
    tok = tok.rstrip('0').rstrip('.')
    if tok == '':
        return Rational(0)
    elif '.' not in tok:
        return Rational(int(tok))
    else:
        int_part, dec_part = tok.split('.')
        pow_ten = 10 ** len(dec_part)
        int_part, dec_part = int(int_part), int(dec_part)
        return Rational(int_part * pow_ten + dec_part, pow_ten)

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

    def eat(self, token_type: 'Union[str, Iterable[str]]' = None) -> 'Token':
        tok = self.current_token
        if isinstance(token_type, str):
            condition = (tok.type == token_type)
        elif isinstance(token_type, Iterable):
            condition = (tok.type in token_type)
        if token_type == None or condition:
            self.current_token = self.lexer.next_token()
            return tok
        else:
            raise UnexpectedTokenError(self.lexer, tok)

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

    # Will produce a matrix for a matline or matfull
    def matrix(self) -> 'Literal':
        tok1 = self.lexer.get_token(1)
        if tok1.type != Token.LBRACK:
            m = Matrix([self.matline()])
        else:
            m = Matrix(self.matfull())
        return Literal(Literal.MATRIX, m)

    def unit_literal(self) -> 'Literal':
        tok = self.eat(Token.LITERAL)
        if is_number(tok.value):
            type = Literal.NUMBER
            value = rational_from_str(tok.value)
        elif is_variable(tok.value):
            if tok.value in self.function_variables:
                type = Literal.FUN_VARIABLE
            else:
                type = Literal.VARIABLE
            value = tok.value
            self.variables_present.add(tok.value)
        else:
            raise Exception("Invalid use of Parse._token_to_unit_litteral")
        return Literal(type, value)

    def function(self) -> 'Literal':
        fname = self.eat(Token.LITERAL).value
        self.eat(Token.LPAR)
        tok = self.current_token
        if tok.type == Token.LITERAL:
            if is_variable(tok.value) and tok.value in self.function_variables:
                raise RecursiveFunctionDefinitonError()
            else:
                arg = self.unit_literal()
        elif tok.type == Token.LBRACK:
            arg = self.matrix()
        else:
            raise UnexpectedTokenError(self.lexer, self.current_token)
        self.eat(Token.RPAR)
        return Literal(Literal.FUNCTION, (fname, arg))

    def eat_optional_sign(self) -> 'str':
        if self.current_token.type in (Token.PLUS, Token.MINUS):
            return self.eat().type
        else:
            return Token.PLUS

    def eat_sign(self) -> 'str':
        return self.eat((Token.PLUS, Token.MINUS)).type

    # (must be signed)    literal: (PLUS | MINUS) (unit_literal | matfull | function)
    # (must'nt be signed) literal: (PLUS | MINUS)? (unit_literal | matfull | function)
    def literal(self, matrix_allowed=True) -> 'Literal':
        tok = self.current_token
        if tok.type == Token.LITERAL:
            if self.lexer.get_token(1).type == Token.LPAR:
                return self.function()
            else:
                return self.unit_literal()
        elif matrix_allowed:
            return self.matrix()
        raise MatrixInMatrixError()

    # factor: literal | LPAREN expr RPAREN
    def factor(self, matrix_allowed=True) -> Union['Literal', 'Expr']:
        tok = self.current_token
        if tok.type == Token.LPAR:
            self.eat()
            res = self.expr(matrix_allowed=matrix_allowed)
            self.eat(Token.RPAR)
        else:
            res = self.literal(matrix_allowed=matrix_allowed)
        return res



    # term: factor ((MATMULT | MULT | DIV | MOD | POW) factor)*
    def term(self, matrix_allowed=True) -> 'Term':

        can_skip_mult_left = lambda: self.current_token.type == Token.LPAR or is_number(self.current_token.value)
        can_skip_mult_right = lambda: is_variable(self.current_token.value) or self.current_token.type == Token.LPAR
        is_term_operation = lambda: self.current_token.type in (Token.MULT, Token.DIV, Token.MOD, Token.MATMULT, Token.POW)
        is_term_factor = lambda: self.current_token.type in (Token.LITERAL, Token.LPAR)

        can_skip_mult = can_skip_mult_left()
        t = Term(self.factor(matrix_allowed=matrix_allowed))
        while True:
            if is_term_operation():
                op = self.eat()
            elif can_skip_mult:
                if can_skip_mult_right():
                    op = Token(Token.MULT, '*')
                else:
                    raise UnexpectedTokenError(self.current_token)
            else:
                raise UnexpectedTokenError(self.current_token)
            f = self.factor(matrix_allowed=matrix_allowed)
            t.push_back(op.type, f)
            can_skip_mult = can_skip_mult_left()
            if not is_term_operation() and not is_term_factor():
                break
        # while self.current_token.type in (Token.MULT, Token.DIV, Token.MOD, Token.MATMULT, Token.POW):
        #     op = self.eat()
        #     f = self.factor(matrix_allowed=matrix_allowed)
        #     t.push_back(op.type, f)
        return t

    # expr: term ((PLUS | MINUS) term)*
    def expr(self, matrix_allowed=True) -> 'Expr':
        sign = self.eat_optional_sign()
        e = Expr()
        t = self.term(matrix_allowed=matrix_allowed)
        t.set_sign(sign)
        e.push_back(t)
        while self.current_token.type in (Token.PLUS, Token.MINUS):
            sign = self.eat_sign()
            t = self.term(matrix_allowed=matrix_allowed)
            t.set_sign(sign)
            e.push_back(t)
        return e

    def expect_eof(self):
        self.eat(Token.EOF)

    def unknown_variables(self):
        return {
            vp for vp in self.variables_present
                if vp not in self.context and vp not in self.function_variables}

    def check_unknown_variables(self):
        unknown_variables = self.unknown_variables()
        if len(unknown_variables) > 0:
            raise UnknownVariablesError(unknown_variables)

