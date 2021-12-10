from typing import Iterable, Union, List, Tuple
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

    def __init__(self, lexer: 'Lexer', context: 'Context' = dict(), function_definition: 'Tuple[str, str]' = None):
        self.lexer: Lexer = lexer
        self.current_token: Token = lexer.next_token()
        self.variables_present = set()
        self.context = context
        self.is_fun_definition = function_definition is not None
        if self.is_fun_definition:
            self.function_name = function_definition[0]
            self.function_variable = function_definition[1]

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
            if self.is_fun_definition and tok.value == self.function_variable:
                type = Literal.FUN_VARIABLE
            else:
                type = Literal.VARIABLE
            value = tok.value
            self.variables_present.add(tok.value)
        else:
            raise Exception("Invalid use of Parse._token_to_unit_litteral")
        return Literal(type, value)

    # ---->
    def function(self) -> 'Literal':
        fname = self.eat(Token.LITERAL).value
        #

        self.eat(Token.LPAR)
        tok = self.current_token
        if tok.type == Token.LITERAL:
            arg = self.expr(matrix_allowed=True)
            # if is_variable(tok.value) and self.is_fun_definition and tok.value == self.function_variable:
            #     raise RecursiveFunctionDefinitonError()
            # else:
            #     arg = self.unit_literal()
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
        # print("MAGAGHCDSHV")
        # print(f"self.current_token={self.current_token}")
        # print(f"self.lexer.get_token(1)={self.lexer.get_token(1)}")
        if tok.type == Token.LITERAL:
            if self.lexer.get_token(1).type == Token.LPAR:
                # print("CANARFUN")
                return self.function()
            else:
                return self.unit_literal()
        elif matrix_allowed:
            return self.matrix()
        raise MatrixInMatrixError()

    # factor: literal | LPAREN expr RPAREN
    def factor(self, matrix_allowed=True) -> Union['Literal', 'Expr']:
        tok = self.current_token
        # print("INVITRO")
        # print(f"self.current_token={self.current_token}")
        if tok.type == Token.LPAR:
            self.eat()
            res = self.expr(matrix_allowed=matrix_allowed)
            self.eat(Token.RPAR)
        else:
            # print("BOOL")
            res = self.literal(matrix_allowed=matrix_allowed)
            # print("BOOLCARRE")
        return res

    # term: factor ((MATMULT | MULT | DIV | MOD | POW) factor)*
    def term(self, matrix_allowed=True) -> 'Term':

        # can_skip_mult_left = lambda: (self.current_token.type in (Token.LPAR, Token.EOF) or is_number(self.current_token.value))
        # can_skip_mult_right = lambda: (is_variable(self.current_token.value) or self.current_token.type == Token.LPAR)
        is_term_operation = lambda: (self.current_token.type in (Token.MULT, Token.DIV, Token.MOD, Token.MATMULT, Token.POW))
        is_term_factor = lambda: (self.current_token.type in (Token.LITERAL, Token.LPAR))

        def can_skip_mult(left, right):
            return is_number(left.value) and is_variable(right.value)

        # print(f"self.current_token={self.current_token}")
        # can_skip_mult = can_skip_mult_left()
        left = self.current_token
        t = Term(self.factor(matrix_allowed=matrix_allowed))
        while is_term_operation() or is_term_factor():
            # print(f"t={t}")
            # print(f"self.current_token={self.current_token}")
            # print(f"can_skip_mult={can_skip_mult}")
            # print(f"can_skip_mult_right()={can_skip_mult_right()}")

            right = self.current_token
            if is_term_operation():
                # print("KOKO")
                op = self.eat()
            # elif can_skip_mult:
            elif can_skip_mult(left, right):
                # if can_skip_mult_right():
                op = Token(Token.MULT, '*')
                # else:
                #     print("COCO")
                #     raise UnexpectedTokenError(self.lexer, self.current_token)
            else:
                # print("HUGO")
                raise UnexpectedTokenError(self.lexer, self.current_token)
            # print("OOF")
            f = self.factor(matrix_allowed=matrix_allowed)
            t.push_back(op.type, f)
            # can_skip_mult = can_skip_mult_left()
            left = self.current_token

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
        res = {vp for vp in self.variables_present
                if vp not in self.context}
        if self.is_fun_definition and self.function_variable in res:
            res.remove(self.function_variable)
        return res

    def check_unknown_variables(self):
        unknown_variables = self.unknown_variables()
        if len(unknown_variables) > 0:
            raise UnknownVariablesError(unknown_variables)

