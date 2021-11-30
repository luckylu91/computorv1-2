
operators_priorities = [['*', '%', '/'], ['+', '-']]

def find_all_matching_operands(toks):
    dict_par = dict()
    dict_brack = dict()
    stack_par = []
    stack_brack = []
    for i, tok in enumerate(toks):
        if tok == '(':
            stack_par.append(i)
        elif tok == '[':
            stack_brack.append(i)
        elif tok == ')':
            if len(stack_par) == 0:
                raise Exception()
            if len(stack_brack) > 0 and stack_brack[-1] > stack_par[-1]:
                raise Exception()
            ilast_par = stack_par.pop(-1)
            dict_par[ilast_par] = i
        elif tok == ']':
            if len(stack_brack) == 0:
                raise Exception()
            if len(stack_par) > 0 and stack_par[-1] > stack_brack[-1]:
                raise Exception()
            ilast_brack = stack_brack.pop(-1)
            dict_brack[ilast_brack] = i
    return dict_par, dict_brack
