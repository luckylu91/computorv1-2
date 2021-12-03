#!/usr/bin/env python3

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
    return (a // p, b // p)

if __name__ == '__main__':
    print(f"pgcd(1, 1) = {pgcd(1, 1)}")
    print(f"pgcd(1, 3) = {pgcd(1, 3)}")
    print(f"pgcd(2, 6) = {pgcd(2, 6)}")
    print(f"pgcd(12, 72) = {pgcd(12, 72)}")
    print(f"pgcd(12, 73) = {pgcd(12, 73)}")
