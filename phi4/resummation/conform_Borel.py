#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from sympy import gamma, binomial
from math import sqrt, exp
from numpy import inf
import scipy.integrate as integrate
from uncertSeries import Series
import matplotlib.pyplot as plt


eps = 0.5  # d = 3
#eps = 1.0  # d = 2

def func(t,a,b,k, eps):
    u = (sqrt(1+a*eps*t)-1)/(sqrt(1+a*eps*t)+1)
    res = t ** b * exp(-t) * u ** (k)
    return res

def conformBorel(coeffs, eps, b = 2.5,):
    A = coeffs
    a, b = 0.238659217, b # -- for d = 2
    #a, b = 0.14777422, 3.5 # -- for d = 3
    B = [A[k]/gamma(k+b+1) for k in range(len(A))] ## образ Бореля-Лероя
    U = [B[0]] + \
        [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(1,k+1)]) for k in range(1,len(B))]
    #print "U =",U
    #for k in range(len(U)):
    #    print "k = %d:"%k,"%f ± %e"%(integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100))
    return [U[k]*integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100)[0] for k in range(len(U)) ]


def plot(coeffs):
    """
    Plot resummed function f(L), where L -- number of loops
    """
    n = len(coeffs)
    plt.clf()
    L = range(2,n)
    coeffs_by_loops = [coeffs[:k] for k in L]
    points = [conformBorel(c,eps) for c in coeffs_by_loops]
    plt.plot(L, points)
    title = 'test'
    plt.title(title)
    plt.legend(['b = 2.5'], loc = "lower left")
    plt.grid(True)
    #plt.ylim(-10,10)
    plt.savefig('pic_1.pdf')

if __name__ == "__main__":
    #import Vladimirov_et_all_1984, Kleinert_book
    #print "Vladimirov:\teta =", sum(conformBorel(Vladimirov_et_all_1984.eta(1), eps))
    #print "Kleinert:\teta =", sum(conformBorel(Kleinert_book.eta(1), eps))
    #print conformBorel(Kleinert_book.eta(1), eps)
    #print "\nTest (Kleinert 17.16):\teta =", sum(conformBorel([0, 0, 0.0185, 0.0187, -0.0083, 0.0257], eps * 2))

    L2, L4 = 5, 6
    Z2   = eval(open('Z2.txt').read())
    Z3   = eval(open('Z3.txt').read())
    beta = eval(open('beta.txt').read())
    eta_g= eval(open('eta.txt').read())

    beta = map(lambda x: x.n, beta.gSeries.values())
    eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    #beta = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    #eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233]
    #Z2 = [1, 0, -0.0084915370, -0.005323936, -0.002340342, -0.00135597, -0.0003502]
    #Z3 = [1, 1.0, 0.624930113, 0.4470878, 0.1735522, 0.283165]
    beta = beta[:L4 + 2]
    eta_g = eta_g[:L2 + 1]
    #print "beta =", beta
    gStar = 1.75
    delta = 0.01
    for i in range(1000):
        g1 = sum(conformBorel(beta, gStar - delta))
        g2 = sum(conformBorel(beta, gStar + delta))
        #print "β(%.2f) = %.4f, β(%.2f) = %.4f" % (gStar - delta, g1, gStar + delta, g2)
        if g1 - g2 > 0:
            gStar -= delta
        else:
            gStar += delta
        if g1 * g2 < 0:
            break
    print "g* =", gStar

    print "η(g*) =", sum(conformBorel(eta_g, gStar))
    print len(beta), "β(g)/2 =", beta
    print len(eta_g), "η(g)/2 =", eta_g



    gamma2 = beta*Z2.diff()/Z2
    gamma4 = beta*Z3.diff()/Z3
    f2 = gamma2/(Series(6,{0:(2,0)})-gamma2)
    f4 = gamma4/(Series(3,{0:(2,0)})-gamma2)
    print "γ₂ = %s \nγ₄ = %s \nf2 = %s \nf4 = %s" %tuple(map(str,[gamma2,gamma4,f2,f4]))

    #ser = 1+f4-f2

    for k2, k4 in [(4, 4), (5, 5), (6, 5)]:
        print "\nL = ", k2, k4
        #_coeffs = ser.coeffs()[:k]
        #print "coeffs =", _coeffs
        _f2 = f2.coeffs()[:k2]
        _f4 = f4.coeffs()[:k4]

        gStar = 0.75
        delta = 0.01
        # b = 2.5
        # b2 = b
        # b4 = b
        b2 = 1.
        b4 = 2.5
        print "b2=%s, b4=%s" % (b2,b4)
        for i in range(1000):
            g1 = 1+sum(conformBorel(_f4, gStar - delta, b4))-sum(conformBorel(_f2, gStar - delta, b2))
            g2 = 1+sum(conformBorel(_f4, gStar + delta, b4))-sum(conformBorel(_f2, gStar + delta, b2))
            #g2 = sum(conformBorel(_coeffs, gStar + delta))
            if i%100 == 0:
                print "β(%.2f) = %.5f, β(%.2f) = %.5f" % (gStar - delta, g1, gStar + delta, g2)
            if abs(g1) > abs(g2):
                gStar += delta
            else:
                gStar -= delta
            if g1 * g2 < 0:
                break
        print "β(%.2f) = %.5f, β(%.2f) = %.5f" % (gStar - delta, g1, gStar + delta, g2)
        print "g* (%d)=" % k4, gStar
        _f2 = f2.coeffs()[:k2]
        _f4 = f4.coeffs()[:k4]
        print _f2, _f4
        print "f2(g*) =", sum(conformBorel(_f2, gStar, b2))
        print "f4(g*) =", sum(conformBorel(_f4, gStar, b4))

