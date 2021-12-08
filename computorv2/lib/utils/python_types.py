from typing import Union, Dict
from ..blocks.expressions import Literal, Expr
from ..blocks.math_types import Rational, Complex, Matrix

Scalar = Union[Rational, Complex]
Context = Dict[str, Union[Rational, Complex, Expr]]
Value = Union[Rational, Complex, Matrix]
Factor = Union[Literal, Expr]
