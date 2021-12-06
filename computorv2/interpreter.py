#!/usr/bin/env python3

import sys
from lib.interpreting import interpret
from lib.blocks.math_types import Complex
from lib.utils.python_types import Context
from lib.errors import Error
import readline # for extended 'input()' function

def try_interpret(line: 'str', context: 'Context', debug: 'bool' = False):
    if len(line.strip()) == 0:
        return
    try:
        interpret(line, context)
        if debug:
            context_str = {k: str(v).replace('\n', ';') for k, v in context.items()}
            print(f"context is now : {context_str}")
    except Error as e:
        print(e)
    print()

context = {'i': Complex.i()}

if len(sys.argv) >= 2:
    fname = sys.argv[1]
    print(f"Interpreting file {fname}")
    with open(fname) as f:
        for line in f.readlines():
            print("> " + line)
            try_interpret(line, context)
else:
    while True:
        line = input('> ')
        try_interpret(line, context)
