#!/usr/bin/env python3
import re

number_pattern = r'\d+(?:\.\d*)?|\.\d+'
x_power_pattern = r'[xX](?:\s*\^\s*(\d+))?'

def _extract_sign(expr, term_index):
	sign_pattern = r'[+-]?' if (term_index == 0) else r'[+-]'
	m = re.match(sign_pattern, expr)
	if m == None:
		raise SyntaxError(f"Unexpected token: {expr[0]}")
	sign = m.group(0)
	expr = expr[m.end(0):].lstrip()
	return expr, sign

def _extract_number(expr):
	m = re.match(number_pattern, expr)
	if m != None:
		coef = float(m.group(0))
		expr = expr[m.end(0):].lstrip()
		if len(expr) == 0 or expr[0] in ('+', '-'):
			return (expr, coef, True)
		if expr[0] != '*':
			raise SyntaxError("Missing a multiplication operator")
		expr = expr[1:].lstrip()
		coef_found = True
	else:
		coef = 1.0
		coef_found = False
	return expr, coef, coef_found

def _extract_x_power(expr):
	m = re.match(x_power_pattern, expr)
	if m != None:
		power = int(m.group(1)) if m.group(1) != None else 1
		expr = expr[m.end(0):].lstrip()
		x_power_found = True
	else:
		power = 0
		x_power_found = False
	return expr, power, x_power_found

def extract_next_term(expr, term_index):
	expr = expr.lstrip()
	# print(f"remaining expr : {expr}")
	expr, sign = _extract_sign(expr, term_index)
	expr, coef, coef_found = _extract_number(expr)
	if sign == '-':
			coef = -coef
	expr, power, x_power_found = _extract_x_power(expr)
	if not coef_found and not x_power_found:
		raise SyntaxError("Unexpected term")
	return (expr, coef, power)



if __name__ == '__main__':
	expr, coef, power = extract_next_term("1", 0)
	assert(expr == '' and coef == 1 and power == 0)
	extract_next_term("- x ^ 2", 1)
	assert(expr == '' and coef == -1 and power == 2)
	extract_next_term("3*x^0", 0)
	assert(expr == '' and coef == 3 and power == 0)

