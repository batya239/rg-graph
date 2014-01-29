#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from sympy import gamma, binomial
import scipy.integrate as integrate

def conformBorel(coeffs):
    A = coeffs
    n = len(A)
    a,b = 0.238659217, 3.5
    B = [aa/gamma(k+b+1) for k,aa in enumerate(A)] ## образ Бореля-Лероя
    U = B[0] + \
        [sum([b*(4/a)**m*binomial(k+m,k-m+1) for m,b in enumerate(B[1:k+1])]) \
            for k in range(1,len(B))]

