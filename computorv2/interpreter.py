#!/usr/bin/env python3

import sys
import argparse
from lib.interpreting import interpret
from lib.blocks.math_types import Complex
from lib.utils.python_types import Context
from lib.utils.errors import Error
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

argparser = argparse.ArgumentParser()
argparser.add_argument("-d", "--debug", help="print context after each action", action="store_true")
argparser.add_argument('file_name', nargs='?', default=None)
args = argparser.parse_args()

context = {'i': Complex.i()}

if args.file_name is not None:
    fname = args.file_name
    print(f"Interpreting file {fname}")
    with open(fname) as f:
        for line in f.readlines():
            print("> " + line)
            try_interpret(line, context, args.debug)
else:
    while True:
        line = input('> ')
        try_interpret(line, context, args.debug)
