#!/usr/bin/env python3

from lib.blocks import Rational, Complex

def tests_rationals():
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


if __name__ == '__main__':
    tests_rationals()
    tests_complex()
