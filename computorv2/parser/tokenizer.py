#!/usr/bin/env python3

import re
from math_types import Rational

tokens_patterns = [
    r'\(', r'\)', r'\[', r'\]', ',', ';',
    r'\+', r'\-', r'\*', r'\*\*', '/', '%', '=',
    r'[a-zA-Z]+', r'\d+(?:\.\d*)?'
]
token_pattern = '|'.join(tokens_patterns)
def tokenize(line):
    return re.findall(token_pattern, line)

is_variable = lambda tok: (re.fullmatch(r'[a-zA-Z]+', tok) != None)
is_number = lambda tok: (re.fullmatch(r'\d+(\.\d*)?', tok) != None)
is_literal = lambda tok: (is_variable(tok) or is_number(tok))

function_pattern = r'\s*([a-zA-Z]+)\s*\(\s*([a-zA-Z]+)\s*\)'
is_function = lambda tok: (re.match(function_pattern, tok) != None)
function_argument_names = lambda tok: re.match(function_pattern, tok).groups()

class Token:
    LITERAL = "LITERAL"
    VARIABLE = "VARIABLE"
    FUNCTION = "FUNCTION"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULT = "MULT"
    MATMULT = "MATMULT"
    DIV = "DIV"
    MOD = "MOD"
    LPAR = "LPAR"
    RPAR = "RPAR"
    LBRACK = "LBRACK"
    RBRACK = "RBRACK"
    COMA = "COMA"
    SEMICOL = "SEMICOL"
    EQUAL = "EQUAL"
    EOF = "EOF"

    def __init__(self, type: str, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, '{self.value}')"

punctuation_dict = {
    '(': Token.LPAR,
    ')': Token.RPAR,
    '[': Token.LBRACK,
    ']': Token.RBRACK,
    ',': Token.COMA,
    ';': Token.SEMICOL,
    '+': Token.PLUS,
    '-': Token.MINUS,
    '*': Token.MULT,
    '**': Token.MATMULT,
    '/': Token.DIV,
    '%': Token.MOD,
    '=': Token.EQUAL
}

class Lexer:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos = -1

    @classmethod
    def eof_token(cl):
        return Token(Token.EOF, None)

    @classmethod
    def str_to_token(cl, s: str):
        if s in punctuation_dict:
            return Token(punctuation_dict[s], s)
        elif is_literal(s):
            return Token(Token.LITERAL, s)
        raise Exception()

    def next_token(self):
        self.pos += 1
        if self.pos >= len(self.tokens):
            return Lexer.eof_token()
        current_token = self.tokens[self.pos]
        return self.str_to_token(current_token)

    def get_token(self, i: int):
        if self.pos + i >= len(self.tokens):
            return Lexer.eof_token()
        return self.str_to_token(self.tokens[self.pos + i])


if __name__ == '__main__':
    lines = [
        "funB(y) = 43 * y / (4.1 % 2. * y)",
        "matA = [[1,2];[3,2];[3,4]]"
    ]
    for line in lines:
        print(f"--- BEGIN LINE {line} ---")
        toks = tokenize(line)
        print(toks)
        lex = Lexer(toks)
        while True:
            tok = lex.next_token()
            print(tok)
            if tok.type == Token.EOF:
                break
        print("--- END LINE ---")
        print()
