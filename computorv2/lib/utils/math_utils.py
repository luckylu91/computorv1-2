def pgcd(a: 'int', b: 'int') -> 'int':
    if a == 0 and b == 0:
        raise Exception()
    a, b = max(a, b), min(a, b)
    if b == 0:
        return a
    if b == 1:
        return 1
    rem = a % b
    while rem != 0:
        a = b
        b = rem
        rem = a % b
    return b

def ppcm(a: 'int', b: 'int') -> 'int':
    return a * b // pgcd(a, b)

def reduce_fraction(a: 'int', b: 'int') -> 'tuple[int, int]':
    p = pgcd(a, b)
    num = a // p
    denum = b // p
    if denum < 0:
        num, denum = -num, -denum
    return (num, denum)
