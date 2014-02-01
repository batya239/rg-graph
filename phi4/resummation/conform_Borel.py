#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from sympy import gamma, binomial
from math import sqrt, exp
from numpy import inf
import scipy.integrate as integrate

eps = 0.5  # d = 3

def func(t,a,b,k, eps):
    u = (sqrt(1+a*eps*t)-1)/(sqrt(1+a*eps*t)+1)
    res = t**b * exp(-t) * u**k
    return res

def conformBorel(coeffs, eps):
    A = coeffs
    #a, b = 0.238659217, 3.5 # -- for d = 2
    a, b = 0.14777422, 3.5 # -- for d = 3
    B = [A[k]/gamma(k+b+1) for k in range(len(A))] ## образ Бореля-Лероя
    U = [B[0]] + \
        [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(1,k+1)]) for k in range(1,len(B))]
    #print "U =",U
    #for k in range(len(U)):
    #    print "k = %d:"%k,"%f ± %e"%(integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100))
    return [U[k]*integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100)[0] for k in range(len(U)) ]

import Vladimirov_et_all_1984, Kleinert_book


print "Vladimirov:\teta =", sum(conformBorel(Vladimirov_et_all_1984.eta(1), eps))
print "Kleinert:\teta =", sum(conformBorel(Kleinert_book.eta(1), eps))
#print conformBorel(Kleinert_book.eta(1), eps)
print "\nTest:\teta =", sum(conformBorel([0, 0, 0.0185, 0.0187, -0.0083, 0.0257], eps))/2