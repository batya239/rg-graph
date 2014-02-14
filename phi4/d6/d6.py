#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'


#!/usr/bin/python

import sympy

d = sympy.var('d')
e = sympy.var('e')

g = sympy.gamma

G = lambda x, y, d: g(d / 2 - x) * g(d / 2 - y) * g(x + y - d / 2) / g(x) / g(y) / g(d - x - y)

G4 = lambda x, y: G(x, y, 4 - 2 * e) / G(1, 1, 4 - 2 * e) / e
G6 = lambda x, y: G(x, y, 6 - 2 * e) / G(1, 1, 6 - 2 * e) / (-6 * e)


def C4(lambdas, n):
    res = g(sum(lambdas) - 2 * n + n * e) * g(2 - 2 * e) ** n / g(e) ** n / g(1 - e) ** (2 * n) / e ** n
    for lambd in lambdas:
        res = res / g(lambd)
    return res


def C6(lambdas, n):
    res = g(sum(lambdas) - 3 * n + n * e) * g(4 - 2 * e) ** n / g(e - 1) ** n / g(2 - e) ** (2 * n) / (-6 * e) ** n
    for lambd in lambdas:
        res = res / g(lambd)
    return res


if __name__ == "__main__":
    print (G4(1, 1) / C4([1, 1], 1) * C6([2, 1], 1) - 2 * G6(2, 1)).series(e, 0, 3).evalf()
    print (G4(1, 1) * G4(1, e) / C4([1, 1, 1], 2) * C6([2, 2, 1], 2) - 3 * G6(2, 1) * G6(2, e)).series(e, 0, 3).evalf()