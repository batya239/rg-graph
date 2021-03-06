#!/usr/bin/python
# -*- coding: utf8

## Borel transform with conformal mapping

__author__ = 'kirienko'

from sympy import gamma, binomial
from math import sqrt
import numpy as np # inf, exp, array, arange
import scipy.integrate as integrate
from scipy.optimize import curve_fit
from uncertSeries import Series
import matplotlib.pyplot as plt


def func(t,a,b,k, eps):
    """
    Образ Бореля
    @param t:
    @param a: из АВП
    @param b: из АВП + что-то
    @param k: номер члена
    @param eps: заряд!
    @return:
    """
    u = (sqrt(1+a*eps*t)-1)/(sqrt(1+a*eps*t)+1)
    res = t ** b * np.exp(-t) * u ** (k)
    return res


def conformBorel(coeffs, eps, b = 2, loops = 6, n = 1, dim = 2):
    A = coeffs
    # print "Initial coeffs:", A
    if dim is 2:
        a, b = 0.238659217,b # -- for d = 2
    elif dim is 3:
        a, b = 0.14777422, b # -- for d = 3
    else:
        raise Exception("Dimension must be either 2 or 3")

    nulls = 0 ## <-- количество начальных нулевых коэффициентов
    for i in A:
        if i == 0: nulls += 1
        else: break
    n = n ## <-- какую степень заряда выносить
    L = loops + nulls - n - 1
    A = A[n:]

    print "A =", A, " len(A)=%d, L=%d"%(len(A),L)
    B = [A[k]/gamma(k+b+1) for k in range(L)] ## образ Бореля-Лероя
    # print "B =",B, " len(B)=%d, L=%d"%(len(B),L)
    U = [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(L)]) for k in range(L)]
    # print "U =",U, " len(U)=%d, L=%d"%(len(U),L)
    return [eps**n*U[k]*integrate.quad(func, 0., np.inf, args=(a, b, k, eps), limit=100)[0] for k in range(L) ]

def findZero(beta_half, gStar = 1.43, delta = 0.01, b = 2):
    _gStar, _b = gStar, b
    #print "β/2 =", beta_half
    for i in range(1000):
        g1 = sum(conformBorel(beta_half, _gStar - delta, loops = len(beta_half)-1, n = 1, b = _b))
        g2 = sum(conformBorel(beta_half, _gStar + delta, loops = len(beta_half)-1, n = 1, b = _b))
        #print "β(%.2f) = %.4f, β(%.2f) = %.4f" % (_gStar - delta, g1, _gStar + delta, g2)
        if abs(g1) > abs(g2):
            _gStar += delta
        else:
            _gStar -= delta
        if g1 * g2 < 0:
            break
    return _gStar


if __name__ == "__main__":
    #import Vladimirov_et_all_1984, Kleinert_book
    #print "Vladimirov:\teta =", sum(conformBorel(Vladimirov_et_all_1984.eta(1), eps))
    #print "Kleinert:\teta =", sum(conformBorel(Kleinert_book.eta(1), eps))
    #print conformBorel(Kleinert_book.eta(1), eps)
    #print "\nTest (Kleinert 17.16):\teta =", sum(conformBorel([0, 0, 0.0185, 0.0187, -0.0083, 0.0257], eps * 2))

    L2, L4 = 6, 5
    N = 1 # 1, 0 -1
    B = 5
    Z2   = eval(open('Z2.txt').read())
    Z3   = eval(open('Z3.txt').read())
    beta = eval(open('beta_n%d.txt'%N).read())
    eta_g= eval(open('eta_n%d.txt'%N).read())

    #beta = map(lambda x: x.n, beta.gSeries.values())
    #eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    beta_half = [0, -1.0, 1.0, -0.71617362, + 0.9307664, -1.582388, 3.26018] ## NB: in fact it's beta/2
    eta_g = [0., 0., 0.033966147, -0.002022555, 0.0113931, -0.0137359, 0.02838]
    #Z2 = [1, 0, -0.0084915370, -0.005323936, -0.002340342, -0.00135597, -0.0003502]
    #Z3 = [1, 1.0, 0.624930113, 0.4470878, 0.1735522, 0.283165]

    #beta_half = [b/2 for b in beta[:L4+2]]
    #eta_g = eta_g[:L2 + 1]
    gStar = findZero(beta_half, b = B)
    print "g* =", gStar

    #print "η(g*):\n", sum(conformBorel(eta_g, 1.88))
    resummed = conformBorel(eta_g, gStar, b = 2)
    print "Resummed:", resummed,[sum(resummed[:j+1]) for j in range(len(resummed))]
    print "η(g*):\n", sum(resummed)

    # print len(beta_half), "β(g)/2 =", beta_half

