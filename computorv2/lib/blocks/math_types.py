from typing import List, Union, Callable

import functools
from ..utils.math_utils import ppcm, reduce_fraction
from ..errors import ConversionError, DifferentMatrixShapeError, \
                     IncompatibleMatrixShapeError, ModuloError, \
                     MatrixDivisionOperatorError, DivisionByZeroError

RationalOrInt = Union['int', 'Rational']
Scalar = Union['Rational', 'Complex']
ScalarOrInt = Union['int', 'Rational', 'Complex']
Value = Union['Rational', 'Complex', 'Matrix']

@functools.total_ordering
class Rational:
    def __init__(self, num: 'int', denum: 'int' = 1):
        num, denum = reduce_fraction(num, denum)
        self.num = num
        self.denum = denum

    @classmethod
    def zero(cl) -> 'Rational':
        return Rational(0)

    @classmethod
    def one(cl) -> 'Rational':
        return Rational(1)

    def __add__(self, other) -> 'Scalar':
        if isinstance(other, Complex) or isinstance(other, Matrix):
            return other + self
        if isinstance(other, int):
            other = Rational(other)
        new_denum = ppcm(self.denum, other.denum)
        return Rational(self.num * new_denum // self.denum + other.num * new_denum // other.denum, new_denum)

    def __neg__(self) -> 'Rational':
        return Rational(-self.num, self.denum)

    def __sub__(self, other: 'Scalar') -> 'Scalar':
        if isinstance(other, Complex):
            return other.__rsub__(self)
        return self + (-other)

    def __mul__(self, other: 'Scalar') -> 'Scalar':
        if isinstance(other, Complex) or isinstance(other, Matrix):
            return other * self
        if isinstance(other, int):
            other = Rational(other)
        return Rational(self.num * other.num, self.denum * other.denum)

    def __truediv__(self, other: 'Scalar') -> 'Scalar':
        if other == 0:
            raise DivisionByZeroError()
        if isinstance(other, Complex) or isinstance(other, Matrix):
            return other.__rtruediv__(self)
        if isinstance(other, int):
            other = Rational(other)
        return Rational(self.num * other.denum, self.denum * other.num)

    def __mod__(self, other: 'Rational') -> 'Rational':
        if isinstance(other, Complex) or isinstance(other, Matrix):
            raise ModuloError(Rational, type(other))
        if isinstance(other, int):
            other = Rational(other)
        return Rational((self.num * other.denum) % (other.num * self.denum), self.denum * other.denum)

    def __eq__(self, other: 'Scalar') -> 'bool':
        if isinstance(other, Rational):
            return self.num == other.num and self.denum == other.denum
        elif isinstance(other, Complex):
            return other.im == 0 and self == other.re
        else:
            assert(isinstance(other, int))
            return self.denum == 1 and self.num == other

    def __gt__(self, other: 'Rational') -> 'bool':
        if isinstance(other, int):
            other = Rational(other)
        return self.num * other.denum > other.num * self.denum

    def __ge__(self, other: 'Rational') -> 'bool':
        if isinstance(other, int):
            other = Rational(other)
        return self.num * other.denum >= other.num * self.denum

    def __radd__(self, other: 'Scalar') -> 'Scalar':
        return self + other

    def __rsub__(self, other: 'Scalar') -> 'Scalar':
        return self - other

    def __rmul__(self, other: 'Scalar') -> 'Scalar':
        return self * other

    def __req__(self, other: 'Scalar') -> 'bool':
        return self == other

    def __rtruediv__(self, other: 'Scalar') -> 'Scalar':
        if isinstance(other, int):
            other = Rational(other)
        return other / self

    def __rmod__(self, other: 'Rational') -> 'Rational':
        if isinstance(other, Complex) or isinstance(other, Matrix):
            raise ModuloError(type(other), Rational)
        if isinstance(other, int):
            other = Rational(other)
        return other % self

    def __str__(self) -> 'str':
        if self.denum == 1:
            return str(self.num)
        return f"{self.num / self.denum:.6f}".rstrip('0').rstrip('.')

    def __repr__(self) -> str:
        return self.__str__()


class Complex:
    def __init__(self, re: 'RationalOrInt', im: 'RationalOrInt' = 0):
        self.re = re if isinstance(re, Rational) else Rational(re)
        self.im = im if isinstance(im, Rational) else Rational(im)

    @classmethod
    def zero(cl) -> 'Complex':
        return Complex(0, 0)

    @classmethod
    def one(cl) -> 'Complex':
        return Complex(1, 0)

    @classmethod
    def i(cl) -> 'Complex':
        return Complex(0, 1)

    @classmethod
    def from_any_value(cl, val: 'ScalarOrInt') -> 'Complex':
        if (isinstance(val, Complex)):
            return val
        if (isinstance(val, Rational) or isinstance(val, int)):
            return Complex(val)
        raise ConversionError(val, Complex)

    @classmethod
    def scalar_from_re_im(cl, re: 'Rational', im: 'Rational') -> 'Scalar':
        if im == 0:
            return re
        return Complex(re, im)

    def __add__(self, other: 'ScalarOrInt') -> 'Scalar':
        other = Complex.from_any_value(other)
        return Complex.scalar_from_re_im(self.re + other.re, self.im + other.im)

    def __neg__(self) -> 'Complex':
        return Complex.scalar_from_re_im(-self.re, -self.im)

    def __sub__(self, other: 'ScalarOrInt') -> 'Scalar':
        other = Complex.from_any_value(other)
        return self + (-other)

    def __mul__(self, other: 'ScalarOrInt') -> 'Scalar':
        other = Complex.from_any_value(other)
        return Complex.scalar_from_re_im(
            self.re * other.re - self.im * other.im,
            self.re * other.im + self.im * other.re)

    def _inverse(self) -> 'Complex':
        d = self.re * self.re + self.im * self.im
        return Complex.scalar_from_re_im(self.re / d, -self.im / d)

    def __truediv__(self, other: 'ScalarOrInt') -> 'Scalar':
        if other == 0:
            raise DivisionByZeroError()
        other = Complex.from_any_value(other)
        return self * other._inverse()

    def __eq__(self, other: 'ScalarOrInt') -> 'bool':
        other = Complex.from_any_value(other)
        return self.re == other.re and self.im == other.im

    def __radd__(self, other: 'ScalarOrInt') -> 'Scalar':
        return self + other

    def __rsub__(self, other: 'ScalarOrInt') -> 'Scalar':
        return self - other

    def __rmul__(self, other: 'ScalarOrInt') -> 'Scalar':
        return self * other

    def __req__(self, other: 'ScalarOrInt') -> 'bool':
        return self == other

    def __rtruediv__(self, other: 'ScalarOrInt') -> 'Scalar':
        return self._inverse() * other

    @classmethod
    def _imginary_part_str(cl, im: 'Rational'):
        if im == 1:
            return 'i'
        else:
            return str(im) + 'i'

    def __str__(self) -> 'str':
        if self.im == 0:
            return str(self.re)
        if self.re == 0:
            return Complex._imginary_part_str(self.im)
        if self.im > 0:
            return f"{str(self.re)} + {Complex._imginary_part_str(self.im)}"
        else:
            return f"{str(self.re)} - {Complex._imginary_part_str(-self.im)}"

    def __repr__(self) -> str:
        return self.__str__()


class Matrix:
    @classmethod
    def shape_is_valid(cl, data: 'List[List]') -> 'bool':
        return len(set(len(line) for line in data)) == 1

    def __init__(self, data: 'List[List]', skip_verif: 'bool' = False):
        if not skip_verif and not Matrix.shape_is_valid(data):
            msg = "All lines in matrix must be of the same size\n"
            msg += f"Matrix is:\n{Matrix.str_from_data(data)}\n"
            msg += f"Sizes of lines {[len(line) for line in data]}"
            raise Exception(msg)
        self.data = data
        self.h = len(data)
        self.w = len(data[0])

    def T(self) -> 'Matrix':
        dataT = [[self.data[j][i] for j in range(self.h)] for i in range(self.w)]
        return Matrix(dataT, skip_verif=True)

    @classmethod
    def verify_same_shape(cl, m1: 'Matrix', m2: 'Matrix', op_name: 'str'):
        if not (m1.h == m2.h and m1.w == m2.w):
            raise DifferentMatrixShapeError(m1, m2, op_name)

    @classmethod
    def verify_can_mult(cl, m1: 'Matrix', m2: 'Matrix'):
        if m1.w != m2.h:
            raise IncompatibleMatrixShapeError(m1, m2)

    @classmethod
    def matmult(cl, m1: 'Matrix', m2: 'Matrix') -> 'Matrix':
        Matrix.verify_can_mult(m1, m2)
        res = []
        for row1 in m1.data:
            res_row = []
            for col2 in m2.T().data:
                res_row.append(sum((v1 * v2 for v1, v2 in zip(row1, col2)), start=Rational.zero()))
            res.append(res_row)
        return Matrix(res, skip_verif=True)

    @classmethod
    def elementwise_operation(cl, operation: 'Callable', m1: 'Matrix', m2: 'Matrix') -> 'Matrix':
        return Matrix([[operation(el1, el2) for el1, el2 in zip(row1, row2)] for row1, row2 in zip(m1.data, m2.data)])

    @classmethod
    def elementwise_unary_operation(cl, operation: 'Callable', m1: 'Matrix') -> 'Matrix':
        return Matrix([[operation(el1) for el1 in row1] for row1 in m1.data])

    def __add__(self, other: 'Value') -> 'Matrix':
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other, "addition")
            return Matrix.elementwise_operation(lambda x, y: x + y, self, other)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x + other, self)

    def __neg__(self) -> 'Matrix':
        return Matrix.elementwise_unary_operation(lambda x: -x, self)

    def __sub__(self, other: 'Value') -> 'Matrix':
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other, "substraction")
            return Matrix.elementwise_operation(lambda x, y: x - y, self, other)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x - other, self)

    def __mul__(self, other: 'Value') -> 'Matrix':
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other, "multiplication")
            return Matrix.elementwise_operation(lambda x, y: x * y, self, other)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x * other, self)

    def __truediv__(self, other: 'Value') -> 'Matrix':
        if isinstance(other, Matrix):
            raise MatrixDivisionOperatorError(self, other)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x / other, self)

    def __eq__(self, other: 'Value') -> 'bool':
        if isinstance(other, Matrix):
            Matrix.verify_same_shape(self, other, "equality")
            return all(Matrix.elementwise_operation(lambda x, y: x == y, self, other).data)
        else:
            return Matrix.elementwise_unary_operation(lambda x: x / other, self)

    def __radd__(self, other: 'Value') -> 'Matrix':
        return self + other

    def __rsub__(self, other: 'Value') -> 'Matrix':
        return self - other

    def __rmul__(self, other: 'Value') -> 'Matrix':
        return self * other

    def __req__(self, other: 'Value') -> 'bool':
        return self == other

    @classmethod
    def str_from_data(cl, data: 'List[List]') -> 'str':
        return "\n".join("[" + ",".join(f" {l} " for l in line) + "]" for line in data)

    def __str__(self) -> 'str':
        return Matrix.str_from_data(self.data)


    def __repr__(self) -> str:
        return self.__str__()
