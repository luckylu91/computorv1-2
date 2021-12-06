
from typing import Dict
from collections import defaultdict

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

