#!/usr/bin/env python3

from math_utils import pgcd, ppcm, reduce_fraction

class Rational:
    def __init__(self, num: int, denum: int = 1):
        num, denum = reduce_fraction(num, denum)
        self.num = num
        self.denum = denum

    @classmethod
    def zero(cl):
        return Rational(0)

    @classmethod
    def one(cl):
        return Rational(1)

    def __add__(self, other):
        new_denum = ppcm(self.denum, other.denum)
        return Rational(self.num * new_denum // self.denum + other.num * new_denum // other.denum, new_denum)

    def __neg__(self):
        return Rational(-self.num, self.denum)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return Rational(self.num * other.num, self.denum * other.denum)

    # def __invert__(self):
    #     return Rational(self.denum, self.num)

    def __truediv__(self, other):
        return Rational(self.num * other.denum, self.denum * other.num)

    def __eq__(self, other) -> bool:
        if isinstance(other, Rational):
            return self.num == other.num and self.denum == other.denum
        else:
            assert(isinstance(other, int))
            return self.denum == 1 and self.num == other

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self - other

    def __rmul__(self, other):
        return self * other

    def __req__(self, other) -> bool:
        return self == other

    def __rtruediv__(self, other):
        return self / other

    def __str__(self):
        if self.denum == 1:
            return str(self.num)
        return f"{self.num / self.denum:.6f}".rstrip('0').rstrip('.')

if __name__ == '__main__':
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
