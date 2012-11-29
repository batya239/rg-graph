#!/usr/bin/python
# -*- coding: utf8
from polynomial.polynomial_product import PolynomialProduct
from polynomial.multiindex import MultiIndex
from polynomial.polynomial import Polynomial

# u1

mi1=MultiIndex({1:2})
P1=Polynomial({mi1:1})
#P1_=Polynomial({mi1:1})

# (u1 u2 +u1 u3 +u2 u3)**(2-e)

mi2=MultiIndex({1:1,2:1})
mi3=MultiIndex({1:1,3:1})
mi4=MultiIndex({2:1,3:1, "a0":1})

P2=Polynomial({mi2:1,mi3:1,mi4:1} , degree=(-2,1))
pp=PolynomialProduct(set([P1, P2]))

mi_u1_1=MultiIndex()
mi_u1_2=MultiIndex({2:1})
mi_u1_3=MultiIndex({3:1})
p_u1=Polynomial({mi_u1_1:1,mi_u1_2:1,mi_u1_3:1},  degree=-1)
pp_u1=PolynomialProduct(set([p_u1]))



print "\ninitial expr"
print pp.__repr__()

pp1_23=pp.stretch(1,[2,3])


print "\nsector 1(2,3)"
print pp1_23
PP_1_23=(pp1_23,pp_u1)

PP_1_23_2_3=map(lambda x:x.stretch(2,[3]), PP_1_23)


print "\nsector 1(2,3),2(3)"
print PP_1_23_2_3

pp_123_23=PP_1_23_2_3[0]

p_diff=pp_123_23.diff("a0")

print

print p_diff