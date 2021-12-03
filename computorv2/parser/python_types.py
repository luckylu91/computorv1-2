from typing import Union, Dict
import expr
import math_types as mt

Scalar = Union['mt.Rational', 'mt.Complex']
Context = Dict[str, Union['mt.Rational', 'mt.Complex', 'expr.Expr']]
Value = Union['mt.Rational', 'mt.Complex', 'mt.Matrix']
