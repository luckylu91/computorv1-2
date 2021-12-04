from typing import Union
from math_types import Rational, Complex, Matrix
from tokenizing import Lexer, is_variable, is_number, tokenize, \
                        is_function, function_argument_names
from expr import Expr
from my_parser import Parser
from errors import WrongEqualSignCount

Value = Union['Rational', 'Complex', 'Matrix']

def expression_from_str(line: 'str', context: 'dict', function_variables: 'set[str]' = set()) -> 'Expr':
    toks = tokenize(line)
    lex = Lexer(toks)
    pars = Parser(lex, context, function_variables)
    e = pars.expr()
    pars.expect_eof()
    return e


def evaluate(line: 'str', context: 'dict') -> 'Value':
    expr = expression_from_str(line, context)
    # print(f"Variables present in expression :\n {{{', '.join(pars.variables_present)}}}")
    return expr.evaluate(context)


def interpret(line, context: 'dict | str'):
    n_equals = line.count('=')
    if n_equals != 1:
        raise WrongEqualSignCount(n_equals)
    left, right = line.split('=')
    left, right = left.strip(), right.strip()
    if right == '?':
        print(evaluate(left, context))
    else:
        if is_variable(left):
            context[left] = evaluate(right, context)
            print(context[left])
        elif is_function(left):
            fun_name, variable_name = function_argument_names(left)
            fun_expr = expression_from_str(right, context, function_variables={variable_name})
            context[fun_name] = (fun_expr, variable_name)
            #....
        else:
            raise Exception()
