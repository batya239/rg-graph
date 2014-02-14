#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from sympy import gamma, binomial
from math import sqrt, exp
from numpy import inf
import scipy.integrate as integrate
from uncertSeries import Series

eps = 0.5  # d = 3
#eps = 1.0  # d = 2

def func(t,a,b,k, eps):
    u = (sqrt(1+a*eps*t)-1)/(sqrt(1+a*eps*t)+1)
    res = t ** b * exp(-t) * u ** (k)
    return res

def conformBorel(coeffs, eps):
    A = coeffs
    a, b = 0.238659217, 3.5 # -- for d = 2
    #a, b = 0.14777422, 3.5 # -- for d = 3
    B = [A[k]/gamma(k+b+1) for k in range(len(A))] ## образ Бореля-Лероя
    U = [B[0]] + \
        [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(1,k+1)]) for k in range(1,len(B))]
    #print "U =",U
    #for k in range(len(U)):
    #    print "k = %d:"%k,"%f ± %e"%(integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100))
    return [U[k]*integrate.quad(func, 0., inf, args=(a, b, k, eps), limit=100)[0] for k in range(len(U)) ]


if __name__ == "__main__":
    import Vladimirov_et_all_1984, Kleinert_book


    print "Vladimirov:\teta =", sum(conformBorel(Vladimirov_et_all_1984.eta(1), eps))
    print "Kleinert:\teta =", sum(conformBorel(Kleinert_book.eta(1), eps))
    #print conformBorel(Kleinert_book.eta(1), eps)
    #print "\nTest (Kleinert 17.16):\teta =", sum(conformBorel([0, 0, 0.0185, 0.0187, -0.0083, 0.0257], eps * 2))

    ## TODO: брать из rg_nikel.py
    L2, L4 = 5, 6
    beta = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233]
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


    from rg_nickel import Z2, Z3, beta

    gamma2 = beta*Z2.diff()/Z2
    gamma4 = beta*Z3.diff()/Z3
    f2 = gamma2/(Series(6,{0:(2,0)})-gamma2)
    f4 = gamma4/(Series(3,{0:(2,0)})-gamma2)
    print "γ₂ = %s \nγ₄ = %s \nf2 = %s \nf4 = %s" %tuple(map(str,[gamma2,gamma4,f2,f4]))

    ser = 1+f4-f2
    #coeffs = map(lambda x: float(x.format('S').split("(")[0]),ser.gSeries.values())

    #f2 = map(lambda x: float(x.format('S').split("(")[0]),f2.gSeries.values())[:6]
    #f4 = map(lambda x: float(x.format('S').split("(")[0]),f4.gSeries.values())[:5]

    for k in range(4,6):
        _coeffs = ser.coeffs()[:k]
        print "coeffs =", _coeffs

        gStar = 0.75
        delta = 0.01
        for i in range(1000):
            g1 = sum(conformBorel(_coeffs, gStar - delta))
            g2 = sum(conformBorel(_coeffs, gStar + delta))
            #print "β(%.2f) = %.4f, β(%.2f) = %.4f" % (gStar - delta, g1, gStar + delta, g2)
            if g1 - g2 < 0:
                gStar -= delta
            else:
                gStar += delta
            if g1 * g2 < 0:
                break
        print "g* (%d)="%k, gStar
        _f2=f2.coeffs()[:k+1]
        _f4=f4.coeffs()[:k]
        print _f2,_f4
        print "f2(g*) =", sum(conformBorel(_f2,gStar))
        print "f4(g*) =", sum(conformBorel(_f4,gStar))