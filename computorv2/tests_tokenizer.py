#!/usr/bin/env python3

from lib.parsing.tokenizing import *

if __name__ == '__main__':
    lines = [
        "funB(y) = 43 * y / (4.1 % 2. * y)",
        "matA = [[1,2];[3,2];[3,4]]",
        "a ** b",
        "a°",
        "2x^2 - 4"
    ]
    for line in lines:
        print(f"--- BEGIN LINE {line} ---")
        try:
            toks = tokenize(line)
        except UnKnownTokenError as e:
            print(e)
        finally:
            print(toks)
            lex = Lexer(toks)
            while True:
                tok = lex.next_token()
                print(tok)
                if tok.type == Token.EOF:
                    break
        print("--- END LINE ---")
        print()
