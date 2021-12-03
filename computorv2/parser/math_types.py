#!/usr/bin/env python3

from typing import Union
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
        if isinstance(other, Complex):
            return other + self
        new_denum = ppcm(self.denum, other.denum)
        return Rational(self.num * new_denum // self.denum + other.num * new_denum // other.denum, new_denum)

    def __neg__(self):
        return Rational(-self.num, self.denum)

    def __sub__(self, other):
        if isinstance(other, Complex):
            return other - self
        return self + (-other)

    def __mul__(self, other):
        if isinstance(other, Complex):
            return other * self
        return Rational(self.num * other.num, self.denum * other.denum)

    # def __invert__(self):
    #     return Rational(self.denum, self.num)

    def __truediv__(self, other):
        if isinstance(other, Complex):
            return Complex(self, 0) / other
        return Rational(self.num * other.denum, self.denum * other.num)

    def __mod__(self, other):
        return Rational((self.num * other.denum) % (other.num * self.denum), self.denum * other.denum)

    def __eq__(self, other) -> bool:
        if isinstance(other, Rational):
            return self.num == other.num and self.denum == other.denum
        elif isinstance(other, Complex):
            return other.im == 0 and self == other.re
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

    def __rmod__(self, other):
        return self % other

    def __str__(self):
        if self.denum == 1:
            return str(self.num)
        return f"{self.num / self.denum:.6f}".rstrip('0').rstrip('.')

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

class Matrix:
    @classmethod
    def shape_is_valid(cl, data):
        return len(set(len(line) for line in data)) == 1

    def __init__(self, data, skip_verif: bool = False):
        if not skip_verif and not Matrix.shape_is_valid(data):
            msg = "All lines in matrix must be of the same size\n"
            msg += f"Matrix is:\n{Matrix.str_from_data(data)}\n"
            msg += f"Sizes of lines {[len(line) for line in data]}"
            raise Exception(msg)
        self.data = data
        self.h = len(data)
        self.w = len(data[0])

    def T(self):
        dataT = [[self.data[j][i] for j in range(self.h)] for i in range(self.w)]
        return Matrix(dataT, skip_verif=True)

    @classmethod
    def verify_same_shape(cl, m1, m2):
        if not (m1.h == m2.h and m1.w == m2.w):
            raise Exception()

    @classmethod
    def verify_can_mult(cl, m1, m2):
        if m1.w != m2.h:
            raise Exception()

    @classmethod
    def matmult(cl, m1, m2):
        Matrix.verify_can_mult(m1, m2)
        res = []
        for row1 in m1.data:
            res_row = []
            for col2 in m2.T().data:
                res_row.append(sum((v1 * v2 for v1, v2 in zip(row1, col2)), start=Rational.zero()))
            res.append(res_row)
        return Matrix(res, skip_verif=True)

    @classmethod
    def elementwise_operation(cl, operation, m1, m2):
        return Matrix([[operation(el1, el2) for el1, el2 in zip(row1, row2)] for row1, row2 in zip(m1.data, m2.data)])

    @classmethod
    def elementwise_unary_operation(cl, operation, m1):
        return Matrix([[operation(el1) for el1 in row1] for row1 in m1.data])

    def __add__(self, other):
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other)
            return Matrix.elementwise_operation(lambda x, y: x + y, self, other)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x + other, self)

    def __neg__(self):
        return Matrix.elementwise_unary_operation(lambda x: -x, self)

    def __sub__(self, other):
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other)
            return Matrix.elementwise_operation(lambda x, y: x - y, self, other)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x - other, self)

    def __mul__(self, other):
        if isinstance(other, Matrix):
            raise Exception()
        else:
            return Matrix.elementwise_unary_operation(lambda x: x * other, self)

    def __truediv__(self, other):
        if isinstance(other, Matrix):
            raise Exception()
        else:
            return Matrix.elementwise_unary_operation(lambda x: x / other, self)

    def __eq__(self, other) -> bool:
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other)
            return all(Matrix.elementwise_operation(lambda x, y: x == y, self, other).data)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x / other, self)

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return self - other

    def __rmul__(self, other):
        return self * other

    def __req__(self, other) -> bool:
        return self == other

    @classmethod
    def str_from_data(cl, data):
        return "\n".join("[" + ",".join(f" {l} " for l in line) + "]" for line in data)

    def __str__(self):
        return Matrix.str_from_data(self.data)


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
