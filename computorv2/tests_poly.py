#!/usr/bin/env python3

from lib.blocks import Poly

if __name__ == '__main__':
    print(Poly.zero())
    print(Poly.one())
    print(Poly.x())
    print(Poly({0: 1, 1: 2, 2: 1}))
