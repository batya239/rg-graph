#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'
import polynomial
import sd_lib


# ee12-e22-e-
D = map(lambda x: (1, x), [(1, 2), (1, 3), (2, 3, 'a0'), ])

P1 = polynomial.poly(D, degree=(-2, 1))
P2 = polynomial.poly([(1, [1, ])])

expr = P1 * P2

# delta function argument
d_arg = polynomial.poly([(1, [1]),
                         (1, [2]),
                         (1, [3])], degree=(1, 0))
print expr

sectors = [
    [(1, [2, 3]), (2, [3,])],
    [(2, [1, 3]), (1, [3,])],
    [(2, [1, 3]), (3, [1,])],
]
for sector in sectors:

# perform variable transformations for given sector
    res = sd_lib.sector_diagram(expr, sector, d_arg)
    print
    print res
    print map(lambda x: x.simplify(), res.diff('a0'))
