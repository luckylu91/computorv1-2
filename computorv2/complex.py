#!/usr/bin/env python3

from rational import Rational
from typing import Union

class Complex:
    def __init__(self, re: Union[int, Rational], im: Union[int, Rational] = 0):
        self.re = re if isinstance(re, Rational) else Rational(re)
        self.im = im if isinstance(im, Rational) else Rational(im)

    @classmethod
    def zero(cl):
        return Complex(0, 0)

    @classmethod
    def one(cl):
        return Complex(1, 0)

    @classmethod
    def i(cl):
        return Complex(0, 1)

    @classmethod
    def from_any_value(cl, val):
        if (isinstance(val, Complex)):
            return val
        if (isinstance(val, Rational) or isinstance(val, int)):
            return Complex(val)
        raise Exception()

    def __add__(self, other):
        other = Complex.from_any_value(other)
        return Complex(self.re + other.re, self.im + other.im)

    def __neg__(self):
        return Complex(-self.re, -self.im)

    def __sub__(self, other):
        other = Complex.from_any_value(other)
        return self + (-other)

    def __mul__(self, other):
        other = Complex.from_any_value(other)
        return Complex(self.re * other.re - self.im * other.im,
                       self.re * other.im + self.im * other.re)

    def _inverse(self):
        d = self.re * self.re + self.im * self.im
        return Complex(self.re / d, -self.im / d)

    def __truediv__(self, other):
        other = Complex.from_any_value(other)
        return self * other._inverse()

    def __eq__(self, other) -> bool:
        other = Complex.from_any_value(other)
        return self.re == other.re and self.im == other.im

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self - other

    def __rmul__(self, other):
        return self * other

    def __req__(self, other) -> bool:
        return self == other

    def __rtruediv__(self, other):
        return self._inverse() * other

    def __str__(self):
        if self.im == 0:
            return str(self.re)
        if self.re == 0:
            return str(self.im) + "i"
        return f"{self.re} + {self.im}i"

if __name__ == '__main__':
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
