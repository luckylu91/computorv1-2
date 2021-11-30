#!/usr/bin/env python3

import sys
from math import sqrt
from equation_parsing import equation_to_coef_list, reduced_form
from print_utils import root_str, print_root

argc = len(sys.argv)
if argc != 2:
	print("Usage : python3 computorv1.py \"(equation expression)\"")
	exit(1)
equation = sys.argv[1]


# Parse the equation

try:
	coef_list = equation_to_coef_list(equation)
except SyntaxError as err:
	print(f"Incorrect equation syntax : {err}")
	exit(1)


# Case '0 = 0'

if len(coef_list) == 0:
	print("The equation simplifies to '0 = 0', solution is the whole real field")
	exit(0)


# Print reduced form and degree

print("Reduced form:", reduced_form(coef_list))
print(f"Polynomial degree: {len(coef_list) - 1}")


# Print solutions depending on degree

if len(coef_list) > 3:
	print("The polynomial degree is strictly greater than 2, I can't solve.")
	exit(0)

elif len(coef_list) == 1:
	print("There is no solution")
	exit(0)

elif len(coef_list) == 2:
	b, a = coef_list
	root = - b / a
	print("The unique solution is:")
	print_root(root)

elif len(coef_list) == 3:
	c, b, a = coef_list
	delta = b ** 2 - 4 * a * c

	if delta > 0:
		delta_sqrt = sqrt(delta)
		root1 = (- b - delta_sqrt) / (2 * a)
		root2 = (- b + delta_sqrt) / (2 * a)
		print("Discriminant is strictly positive, the two solutions are:")
		print_root(root1)
		print_root(root2)

	elif delta == 0:
		root = - b / (2 * a)
		print("Discriminant is zero, the unique solution is:")
		print_root(root)

	else:
		delta_sqrt_abs = sqrt(abs(delta))
		real = - b / (2 * a)
		imag = delta_sqrt_abs / (2 * a)
		print("Discriminant is strictly negative (no real solution), the two complex solutions are:")
		if real != 0:
			print(f"{root_str(real)} + {root_str(abs(imag))} * i")
			print(f"{root_str(real)} - {root_str(abs(imag))} * i")
		else:
			print(f"{root_str(abs(imag))} * i")
			print(f"-{root_str(abs(imag))} * i")


