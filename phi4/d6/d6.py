#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

from rggraphenv import symbolic_functions
import swiginac
e = symbolic_functions.e


d = symbolic_functions.var('d')
gamma = symbolic_functions.tgamma

G = lambda x, y, d: gamma(d / 2 - x) * gamma(d / 2 - y) * gamma(x + y - d / 2) / gamma(x) / gamma(y) / gamma(d - x - y)

G4 = lambda x, y: G(x, y, 4 - 2 * e) / G(1, 1, 4 - 2 * e) / e
G6 = lambda x, y: G(x, y, 6 - 2 * e) / G(1, 1, 6 - 2 * e) / (-6 * e)


def C4(lambdas, n):
    res = gamma(sum(lambdas) - 2 * n + n * e) * gamma(2 - 2 * e) ** n / gamma(e) ** n / gamma(1 - e) ** (2 * n) / e ** n
    for lambd in lambdas:
        if lambd !=0:
            res = res / gamma(lambd)
    return res


def C6(lambdas, n):
    res = gamma(sum(lambdas) - 3 * n + n * e) * gamma(4 - 2 * e) ** n / gamma(e - 1) ** n / gamma(2 - e) ** (2 * n) / (-6 * e) ** n
    for lambd in lambdas:
        if lambd !=0:
            res = res / gamma(lambd)
    return res


if __name__ == "__main__":
    print symbolic_functions.series((G4(1, 1) / C4([1, 1], 1) * C6([2, 1], 1) - 2 * G6(2, 1)), e, 0, 3).evalf()
    print symbolic_functions.series((G4(1, 1) * G4(1, e) / C4([1, 1, 1], 2) * C6([2, 2, 1], 2) - 3 * G6(2, 1) * G6(2, e)), e, 0, 3).evalf()