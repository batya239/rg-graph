#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from sympy import symbols, zeta, poly

n, eps, eta = symbols('n eps eta')

def z(k):
    return float(zeta(k))

def eta(k):
    _eta = (n+2)/(2*(n+8)**2)*(2*eps)**2 * \
        (1 + 2*eps/(4*(n+8)**2) * (-n*n+56*n+272) - (2*eps)**2/(16*(n+8)**4) * \
            (5*n**4+230*n**3-1124*n**2-17920*n-46144+384*z(3)*(n+8)*(5*n+22)) \
            - (2*eps)**3/(64*(n+8)**6) * \
            (13*n**6+946*n**5+27620*n**4+121472*n**3-262528*n**2-5655552 \
                -z(3)*(n+8)*16*(n**5+10*n**4+1220+n**3-1136*n**2-68672*n-171264) \
                +z(4)*(n+8)**3*1152*(5*n+22)-z(5)*(n+8)**2*5120*(2*n**2+55*n+186)))
    eta_k = poly(_eta.subs(n,k).expand()).all_coeffs()
    eta_k.reverse()
    return eta_k