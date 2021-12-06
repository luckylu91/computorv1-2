#!/usr/bin/env python3

from lib.utils.math_utils import pgcd

if __name__ == '__main__':
    print(f"pgcd(1, 1) = {pgcd(1, 1)}")
    print(f"pgcd(1, 3) = {pgcd(1, 3)}")
    print(f"pgcd(2, 6) = {pgcd(2, 6)}")
    print(f"pgcd(-2, 6) = {pgcd(-2, 6)}")
    print(f"pgcd(2, -6) = {pgcd(2, -6)}")
    print(f"pgcd(12, 72) = {pgcd(12, 72)}")
    print(f"pgcd(12, 73) = {pgcd(12, 73)}")
