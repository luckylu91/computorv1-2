from typing import Union, Tuple

from .blocks.expressions import Expr
from .blocks.math_types import Rational, Complex, Matrix
from .parsing.tokenizing import Lexer, Token, is_variable, tokenize, \
                                is_function, function_argument_names
from .parsing.parser import Parser
from .utils.errors import WrongEqualSignCount, NonPolynomialEquation

Value = Union['Rational', 'Complex', 'Matrix']


def expression_from_str(line: 'str', context: 'dict', function_definition: 'Tuple[str, str]' = None) -> 'Expr':
    toks = tokenize(line)
    lex = Lexer(toks)
    pars = Parser(lex, context, function_definition)
    e = pars.expr()
    pars.expect_eof()
    ####
    e.replace(context)
    ####
    pars.check_unknown_variables()
    # print(f"Expression : {e}")
    return e

def expression_and_variables_from_str(line: 'str', context: 'dict'):
    toks = tokenize(line)
    lex = Lexer(toks)
    pars = Parser(lex, context)
    e = pars.expr()
    e.replace(context)
    return e, pars.unknown_variables()


def evaluate(line: 'str', context: 'dict') -> 'Value':
    expr = expression_from_str(line, context)
    return expr.evaluate(context)


def interpret(line, context: 'dict | str'):
    n_equals = line.count('=')
    if n_equals != 1:
        raise WrongEqualSignCount(n_equals)
    left, right = line.split('=')
    left, right = left.strip(), right.strip()

    if right == '?':
        print(evaluate(left, context))

    elif right.endswith('?'):
        right = right[:-1]
        left_expr, left_variables = expression_and_variables_from_str(left, context)
        right_expr, right_variables = expression_and_variables_from_str(right, context)
        assert(len(left_variables.union(right_variables)) <= 1)
        
        right_expr.apply_sign(Token.MINUS)
        left_expr.extend(right_expr)
        left_expr.replace(context)
        left_expr = left_expr.fun_expanded(context)
        left_expr.do_modulos()
        # print(f"expr is polynomial: {left_expr.is_polynomial()}")
        if left_expr.is_polynomial():
            poly = left_expr.to_polynomial()
            poly.print_solutions()
        else:
            raise NonPolynomialEquation()

    else:
        if is_variable(left):
            context[left] = evaluate(right, context)
            print(context[left])

        elif is_function(left):
            fun_name, variable_name = function_argument_names(left)

            fun_expr = expression_from_str(right, context, function_definition=(fun_name, variable_name))
            fun_expr.replace(context)
            fun_expr = fun_expr.fun_expanded(context)

            context[fun_name] = (fun_expr, variable_name)
            if fun_expr.is_polynomial():
                print("IS POLYNOMIAL")
                poly = fun_expr.to_polynomial()
                print(poly.__str__(variable_name=variable_name))
                print(f"poly dict : {poly.d}")
            else:
                print(fun_expr)
            #....
        else:
            raise Exception()
