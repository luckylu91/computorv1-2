from tokenizing import Token
from math_types import Matrix, Rational

def matmult(a, b):
    if not isinstance(a, Matrix) or not isinstance(b, Matrix):
        raise Exception()
    return Matrix.matmult(a, b)

# def do_op(op: 'Token', l1: 'Literal', l2: 'Literal'):
def do_op(op: 'str', l1, l2):
    # print(f"Doing {l1} {op.value} {l2}")
    if l1 is None:
        return l2
    elif l2 is None:
        return l1
    if op == Token.PLUS:
        return l1 + l2
    elif op == Token.MINUS:
        return l1 - l2
    elif op == Token.MULT:
        return l1 * l2
    elif op == Token.DIV:
        return l1 / l2
    elif op == Token.MOD:
        return l1 % l2
    elif op == Token.MATMULT:
        return matmult(l1, l2)

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

def new_sign(sign1: 'str', sign2: 'str'):
    if sign1 == sign2:
        return Token.PLUS
    else:
        return Token.MINUS
