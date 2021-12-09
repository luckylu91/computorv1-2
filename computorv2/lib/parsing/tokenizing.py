#!/usr/bin/env python3

import re
from ..utils.errors import UnKnownTokenError

tokens_patterns = [
    r'\(', r'\)', r'\[', r'\]', ',', ';',
    r'\+', r'\-', r'\*{1,2}', '/', '%', r'\^', '=',
    r'[a-zA-Z]+', r'\d+(?:\.\d*)?', r'\S'
]
token_pattern = '|'.join(tokens_patterns)
token_pattern_valid = '|'.join(tokens_patterns[:-1])
def tokenize(line):
    tokens = re.findall(token_pattern, line)
    for token in tokens:
        if not re.fullmatch(token_pattern_valid, token):
            raise UnKnownTokenError(token)
    return tokens

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
    POW = "POW"
    LPAR = "LPAR"
    RPAR = "RPAR"
    LBRACK = "LBRACK"
    RBRACK = "RBRACK"
    COMA = "COMA"
    SEMICOL = "SEMICOL"
    EQUAL = "EQUAL"
    EOF = "EOF"

    def __init__(self, type: 'str', value: 'str') -> None:
        self.type = type
        self.value = value

    def __str__(self) -> None:
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
    '^': Token.POW,
    '=': Token.EQUAL
}
tokens_str = {t: s for s, t in punctuation_dict.items()}

class Lexer:
    def __init__(self, tokens: 'list') -> None:
        self.tokens = tokens
        self.pos = -1

    @classmethod
    def eof_token(cl) -> 'Token':
        return Token(Token.EOF, None)

    @classmethod
    def str_to_token(cl, s: 'str') -> 'Token':
        if s in punctuation_dict:
            return Token(punctuation_dict[s], s)
        assert(is_literal(s))
        return Token(Token.LITERAL, s)

    def next_token(self) -> 'Token':
        self.pos += 1
        if self.pos >= len(self.tokens):
            return Lexer.eof_token()
        current_token = self.tokens[self.pos]
        return self.str_to_token(current_token)

    def get_token(self, i: 'int') -> 'Token':
        if self.pos + i >= len(self.tokens):
            return Lexer.eof_token()
        return self.str_to_token(self.tokens[self.pos + i])
