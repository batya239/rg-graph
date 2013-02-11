#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'
import polynomial
import sd_lib


# ee12-ee3-333--
D = map(lambda x: (1, x), [(1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4, 'a0'), ])

P1 = polynomial.poly(D, degree=(-1.5, 0))
P2 = polynomial.poly([(1, [1, 1])])

expr = P1 * P2

# delta function argument
d_arg = polynomial.poly([(1, [1]),
                         (1, [2]),
                         (1, [3]),
                         (1, [4])], degree=(1, 0))
print expr
sectors = [
    [(1, [2, 3, 4]), (2, [3, 4]), (3, [4, ])],
    [(2, [1, 3, 4]), (1, [3, 4]), (3, [4, ])],
    [(2, [1, 3, 4]), (3, [1, 4]), (1, [4, ])],
    [(2, [1, 3, 4]), (3, [1, 4]), (4, [1, ])]
]

for sector in sectors:
    # perform variable transformations for given sector
    res = sd_lib.sector_diagram(expr, sector, d_arg)
    print
    print res
    print map(lambda x: x.simplify(), res.diff('a0'))
