from term_parsing import extract_next_term

def _insert_sorted(coef_list, coef, power):
	if power >= len(coef_list):
		coef_list.extend(0 for _ in range(len(coef_list), power + 1))
	coef_list[power] += coef


def _expression_to_coef_list(expr):
	expr = expr.strip()
	if expr == '':
		raise SyntaxError("At least one side is empty")
	if expr == '0':
		return []
	coef_list = []
	i = 0
	while len(expr) > 0:
		expr, coef, power = extract_next_term(expr, i)
		_insert_sorted(coef_list, coef, power)
		i += 1
	return coef_list

def equation_to_coef_list(equation):
	equation = equation.strip()
	if equation == '':
		raise SyntaxError("Empty equation")
	splitted = equation.split('=')
	if len(splitted) != 2:
		raise SyntaxError("Too many '='")
	lhs, rhs = splitted
	poly1 = _expression_to_coef_list(lhs)
	poly2 = _expression_to_coef_list(rhs)
	if poly1 == None or poly2 == None:
		raise SyntaxError("")
	if len(poly2) > len(poly1):
		poly1.extend(0 for _ in range(len(poly1), len(poly2) + 1))
	for i, c in enumerate(poly2):
		poly1[i] -= c
	for i in range(len(poly1) - 1, -1, -1):
		if poly1[i] == 0:
			poly1.pop(i)
		else:
			break
	return poly1

def reduced_form(coef_list):
	expr_list = []
	first_non_zero = True
	for power, coef in enumerate(coef_list):
		if coef == 0:
			continue
		if first_non_zero:
			if coef < 0:
				expr_list.append('-')
			first_non_zero = False
		else:
			expr_list.append('+ ' if coef >= 0 else '- ')
		expr_list.append(f'{abs(coef)} * X^{power} ')
	expr_list.append('= 0')
	return ''.join(expr_list)
