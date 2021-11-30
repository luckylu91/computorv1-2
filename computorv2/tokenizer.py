#!/usr/bin/env python3

import re

tokens = [r'\(', r'\)', r'\[', r'\]', ',', ';', r'\+', r'\-', r'\*', '/', '%', '=', r'\w+', r'\d+']
token_pattern = '|'.join(tokens)

def tokenize(line):
    return re.findall(token_pattern, line)

if __name__ == '__main__':
    toks = re.findall(token_pattern, "funB(y) = 43 * y / (4 % 2 * y)")
    print(toks)
    toks = re.findall(token_pattern, "varA = [[2,3];[4,3]]")
    print(toks)
