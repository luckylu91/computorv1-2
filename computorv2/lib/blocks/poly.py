
from typing import ClassVar, Dict
from collections import defaultdict
from math import sqrt

from .math_types import Rational
from ..utils.python_types import Scalar

class Poly:
    def __init__(self, d: 'Dict[int, Scalar]' = dict()) -> None:
        self.d = {i: v for i, v in d.items() if not (v == 0)}

    @classmethod
    def zero(cl):
        return Poly()

    @classmethod
    def one(cl):
        return Poly({0: 1})

    @classmethod
    def x(cl):
        return Poly({1: 1})

    def __add__(self, other: 'Poly') -> 'Poly':
        d = defaultdict(Rational.zero)
        for i, v in [*self.d.items(), *other.d.items()]:
            d[i] = d[i] + v
        return Poly(d)

    def __mul__(self, other: 'Poly') -> 'Poly':
        d = defaultdict(Rational.zero)
        for i, v1 in self.d.items():
            for j, v2 in other.d.items():
                d[i + j] = d[i + j] + v1 * v2
        return Poly(d)

    def __neg__(self):
        return Poly({i: -v for i, v in self.d.items()})

    def degree(self) -> 'int':
        return

    @classmethod
    def float_str(cl, val: 'float') -> None:
        return f"{val:.6f}".rstrip('0').rstrip('.')

    def print_solutions(self) -> None:
        degree = max(self.d.keys())
        d_float = {i: float(v) for i, v in self.d.items()}

        if degree == 0:
            print("The equation simplifies to '0 = 0', solution is the whole real field")
            exit(0)

        # Print reduced form and degree
        print(f"Reduced form: {self}")
        print(f"Polynomial degree: {degree - 1}")

        # Print solutions depending on degree
        if degree > 2:
            print("The polynomial degree is strictly greater than 2, I can't solve.")
            exit(0)

        elif degree == 0:
            print("There is no solution")
            exit(0)

        elif degree == 1:
            b = 0 if 0 not in d_float else d_float[0]
            a = d_float[1]
            root = - b / a
            print("The unique solution is:")
            print(Poly.float_str(root))

        elif degree == 2:
            c = 0 if 0 not in d_float else d_float[0]
            b = 0 if 1 not in d_float else d_float[1]
            a = d_float[2]

            delta = b ** 2 - 4 * a * c

            if delta > 0:
                delta_sqrt = sqrt(delta)
                root1 = (- b - delta_sqrt) / (2 * a)
                root2 = (- b + delta_sqrt) / (2 * a)
                print("Discriminant is strictly positive, the two solutions are:")
                print(Poly.float_str(root1))
                print(Poly.float_str(root2))

            elif delta == 0:
                root = - b / (2 * a)
                print("Discriminant is zero, the unique solution is:")
                print(Poly.float_str(root))

            else:
                delta_sqrt_abs = sqrt(abs(delta))
                real = - b / (2 * a)
                imag = delta_sqrt_abs / (2 * a)
                print("Discriminant is strictly negative (no real solution), the two complex solutions are:")
                if real != 0:
                    print(f"{Poly.float_str(real)} + {Poly.float_str(abs(imag))} * i")
                    print(f"{Poly.float_str(real)} - {Poly.float_str(abs(imag))} * i")
                else:
                    print(f"{Poly.float_str(abs(imag))} * i")
                    print(f"-{Poly.float_str(abs(imag))} * i")

    def __str__(self):
        if len(self.d) == 0:
            return "0"
        strs = []
        for i, v in sorted(self.d.items(), key=lambda x: x[0], reverse=True):
            s = ""
            if i == 0 or v != 1:
                s += str(v)
            if i >= 1:
                if v != 1:
                    s += "*"
                s += "x"
                if i >=2:
                    s += "^" + str(i)
            strs.append(s)
        return ' + '.join(strs)

    def __repr__(self) -> str:
        return self.__str__()

