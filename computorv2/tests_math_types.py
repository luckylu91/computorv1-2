#!/usr/bin/env python3

from lib.blocks.math_types import Rational, Complex
from lib.utils.errors import Error

def tests_rationals():
    print("--- Tests Rationals ---")
    r = Rational(12, 1)
    print(r)
    r = Rational(12, 6)
    print(r)
    r = Rational(1, 3)
    print(r)
    r = Rational(1, 3) + Rational(1, 2)
    print(r)
    r = Rational(1, 3) - Rational(1, 2)
    print(r)
    r = Rational(1, 3) * Rational(1, 2)
    print(r)
    r = Rational(1, 3) / Rational(1, 2)
    print(r)


def tests_complex():
    print("--- Tests Complex ---")
    c = Complex(1)
    print(c)
    c = Complex(1, 1)
    print(c)
    c = Complex(Rational(1, 2), Rational(22, 21))
    print(c)
    c = Complex(1, 1) * Complex(1, 1)
    print(c)
    c = 5 + 2 * Complex.i()
    print(c)
    c = (1 + Complex.i()) / (1 + Complex.i())
    print(c)
    c = (1 + Complex.i()) / 2
    print(c)
    c = 1 / (1 + Complex.i())
    print(c)
    c = 1 / Complex.i()
    print(c)

def tests_pow():
    def try_print(expr_str):
        try:
            print(eval(expr_str))
        except Error as e:
            print(e)

    print("--- Tests Pow ---")
    print(Rational(2) ** 3)
    print(Complex(0, 1) ** 3)
    print(Rational(2) ** Complex(3, 0))
    try_print("Rational(2) ** Complex(0, 1)")
    try_print("Rational(2) ** Rational(1, 2)")
    try_print("Rational(2) ** (Rational(5, 2) + Rational(1, 2))")
    try_print("Rational(2) ** (Rational(7, 2) - Rational(1, 2))")



if __name__ == '__main__':
    tests_rationals()
    print()
    tests_complex()
    print()
    tests_pow()
