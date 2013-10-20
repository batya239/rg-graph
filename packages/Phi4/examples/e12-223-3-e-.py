#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'
import swiginac
from phi4.symbolic_functions import e, l, series, G

gamma = swiginac.tgamma
euler = swiginac.Euler
pi = swiginac.Pi
z = swiginac.zeta
a = swiginac.symbol('a')

g11 = gamma(l) ** 2 * gamma(1 - l) / gamma(2 * l)

#print series(g11, e, 0, 3)
print "e1111-e-"
a1 = gamma(1 - e) ** 4 * gamma(3 * e - 2) / gamma(4 - 4 * e)
print series(a1, e, 0, 3).expand()
a1_ = swiginac.exp(-3 * euler * e) / ((1 - 4 * e) * (3 - 4 * e) * (1 - 3 * e) * (2 - 3 * e) * (1 - 2 * e)) * (1 / e / 6 - pi ** 2*e/24 - 29 * e * e * z(3) / 6)
print series(a1_, e, 0, 3).expand()
print series(a1 - a1_, e, 0, 3).expand()

a1__ = G(1, 1) ** 2 * G(e, e)
print series(a1__ * (e * g11) ** 3, e, 0, 3).expand()
print series(a1__ * (e * g11) ** 3-a1, e, 0, 3).expand()


print "e12-223-3-e-"
b1_ = swiginac.exp(-3 * euler * e) * (1 / e**3/ 3
                                      +7/e/e/3
                                      +1/e*(swiginac.numer(31)/3-pi**2/12)+(swiginac.numer(103)/3-7*pi**2/12+7*z(3)/3)+ e*(swiginac.numer(235)/3 -31*pi**2/12+49*z(3)/3+5*pi**4/96)
                                      +e*e*(swiginac.numer(19)/3-103*pi**2/12+289*z(3)/3+35*pi**4/96-7*pi**2*z(3)/12+599*z(5)/5)
                                      +e**3*(-swiginac.numer(3953)/3-235*pi**2/12+1729*z(3)/3+967*pi**4/480-49*pi**2*z(3)/12+4193*z(5)/5+108481*pi**6/362880-599*z(3)**2/6))

print series(b1_/(e*g11)**3,e,0,4).expand()
print series(b1_/(e*g11)**3,e,0,4).expand().evalf()

print "-----------------"

print series(((20.7385551028674 - 37.866830505981674047*e)*G(1+3*e,1)*G(1+4*e,1)),e,0,0).evalf()
print series(((20.7385551028674 - 37.866830505981674047*e)*G(1+3*e,1)),e,0,0).evalf()/e

print series(series(((20.7385551028674 - 37.866830505981674047*e)*G(1+3*e,1)*G(1+4*e,1)),e,0,0).evalf()-series(((20.7385551028674 - 37.866830505981674047*e)*G(1+3*e,1)),e,0,0,remove_order=True).evalf()/e,e,0,0).expand()
print ( swiginac.numer(1)/378*(pi**6-(75.6000000000000042)*z(3)**2+1134*z(5))*e**(-1)-4*z(5)*e**(-2)).evalf()