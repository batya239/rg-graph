#!/usr/bin/python
# -*- coding: utf8
from polynomial.polynomial import poly
from polynomial.formatter import format, HUMAN, PYTHON, CPP
from polynomial.polynomial_product import poly_prod


# u1**2
P1 = poly([(1, [1, 1])])
# (u1 u2 + u1 u3 + u2 u3)**(-2+e)
P2 = poly([(1, [2, 3, "a0"]), (1, [1, 3]), (1, [1, 2])], degree=(-2, 1))
# P1 * P2
PP = P1 * P2

# (1 + u2 + u3)**(-1)
P1_u1 = poly([(1, []), (1, [2]), (1, [3])], degree=-1)
PP_u1 = P1_u1.toPolyProd()

print "\ninitial expression"
print PP.__repr__()

PP1_23 = PP.stretch(1, [2, 3])

print "\nsector 1(2,3)"
print PP1_23
PP_1_23 = (PP1_23, PP_u1)

PP_1_23_2_3 = map(lambda x: x.stretch(2, [3]), PP_1_23)

print "\nsector 1(2,3),2(3)"
print PP_1_23_2_3

PP_123_23 = PP_1_23_2_3[0]

PP_diff = PP_123_23.diff("a0")

print "\ndifferential"
print HUMAN, format(PP_diff, HUMAN)[0]
print PYTHON, format(PP_diff, PYTHON)[0]
print CPP, format(PP_diff, CPP)[0]

print "\nvariables"
print PP_diff[0].getVarsIndexes()

print "\nsimplifying"
PP_diff[0] = PP_diff[0].simplify()
print PP_diff[0]

print "\nepsilon expansion of %s" % PP_diff[0]
print PP_diff[0].epsExpansion(1)