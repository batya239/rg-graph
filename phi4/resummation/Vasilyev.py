#!/usr/bin/python
# -*- coding: utf8

"""
Васильев,
    стр. 338, формула (7а)
    стр. 339, формула (8) с точностью до замены 2*eps → eps
"""

__author__ = 'kirienko'

from sympy import symbols, zeta, poly

n, u = symbols('n u')

def z(k):
    return float(zeta(k))

def gamma(k):
    _gamma = u**2 *(n+2)/36 - u**3 * (n+2)*(n+8)/432 + \
    5*u**4*(n+2)/5184* (-n**2+18*n+100) - \
    u**5*(n+2)/186624 * (39*n**3 + 296*n**2+22752*n+77056 - \
    48* z(3) * (n**3-6*n**2+64*n+184) + 1152*z(4)*(5*n+22))
    gamma_k = poly(_gamma.subs(n,k).expand()).all_coeffs()
    gamma_k.reverse()
    gamma_k = [2*g for g in gamma_k]
    return gamma_k

def uStar(eps):
    return float(eps)/3 + eps**2 * 17./81 + float(eps**3)/27 * (709./648 - 4*z(3)) + \
        float(eps**4)/81 * (10909./11664 -106./9 * z(3) - 6*z(4) + 40*z(5))

if __name__ == "__main__":

    print "gamma = ",gamma(1)
    print "u* =", uStar(1)