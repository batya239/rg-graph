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
    res = t**b*exp(-t) * u**k
    return res

def conformBorel(coeffs):
    A = coeffs
    n = len(A)
    #a, b = 0.238659217, 3.5 # -- for d = 2
    a, b = 0.14777422, 2.5 # -- for d = 3
    B = [aa/gamma(k+b+1) for k, aa in enumerate(A)] ## образ Бореля-Лероя
    U = [B[0]] + \
        [sum([b*(4/a)**(m+1)*binomial(k+m,k-m+1) for m,b in enumerate(B[1:k+1])]) \
            for k in range(1,len(B))]
    print "U =",U
    for k in range(len(U)):
        print "%f ± %e"%(integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100))
    return [U[k]*integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100)[0] for k in range(len(U)) ]

from Vladimirov_et_all_1984 import eta_n1

A = conformBorel(eta_n1)
print "A(ϵ) =", " + ".join(map(lambda (k,x): str(x)+"×ϵ^"+str(k), enumerate(A)))
print "eta =",sum([a*eps**k for k,a in enumerate(A)])