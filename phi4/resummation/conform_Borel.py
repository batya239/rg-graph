#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from sympy import gamma, binomial
from math import sqrt
import numpy as np # inf, exp, array, arange
import scipy.integrate as integrate
from scipy.optimize import curve_fit
from uncertSeries import Series
import matplotlib.pyplot as plt


eps = 0.5  # d = 3
#eps = 1.0  # d = 2

def func(t,a,b,k, eps):
    """
    Образ Бореля
    @param t:
    @param a:
    @param b:
    @param k:
    @param eps:
    @return:
    """
    u = (sqrt(1+a*eps*t)-1)/(sqrt(1+a*eps*t)+1)
    res = t ** b * np.exp(-t) * u ** (k)
    return res

def fit_exp(x, a, b, c, x_0):
    #print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a*np.exp(-b*(x-x_0)) + c

def fit_hyperbola(x, a, b, c, x_0):
    #print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a/(x-x_0)**b + 1.75

def conformBorel(coeffs, eps, b = 2.5,):
    A = coeffs
    a, b = 0.238659217, b # -- for d = 2
    #a, b = 0.14777422, 3.5 # -- for d = 3
    B = [A[k]/gamma(k+b+1) for k in range(len(A))] ## образ Бореля-Лероя
    U = [B[0]] + \
        [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(1,k+1)]) for k in range(1,len(B))]
    return [U[k]*integrate.quad(func, 0., np.inf, args=(a, b, k, eps), limit=100)[0] for k in range(len(U)) ]

def findZero(beta_half, gStar = 1.75, delta = 0.01):
    _gStar = gStar
    #print "β/2 =", beta_half
    for i in range(1000):
        g1 = sum(conformBorel(beta_half, _gStar - delta))
        g2 = sum(conformBorel(beta_half, _gStar + delta))
        #print "β(%.2f) = %.4f, β(%.2f) = %.4f" % (_gStar - delta, g1, _gStar + delta, g2)
        if abs(g1) > abs(g2):
            _gStar += delta
        else:
            _gStar -= delta
        if g1 * g2 < 0:
            break
    return _gStar

def plot(coeffs, beta_half, name, fileName):
    """
    Plot resummed function f(L), where L -- number of loops.
    Syntax: plot(coeffs, g*, title, fileName_to_save)
    """
    font = {'family' : 'serif',
            'color'  : 'darkred',
            'weight' : 'normal',
            'size'   : 16,
            }
    plt.clf()
    b_0 = 0
    n = len(coeffs)

    L = range(2,n)
    coeffs_by_loops = [coeffs[:k+1] for k in L]
    plots = []
    gStar_by_loops = [findZero(b) for b in [beta_half[:i] for i in range(4,8)]]
    if len(coeffs_by_loops) > len(gStar_by_loops):##
        gStar_by_loops.append(gStar_by_loops[-1])

    for i in range(4): ## loop over b: b=b_0+i
        points = [sum(conformBorel(c,gStar_by_loops[j],b=b_0+i)) for j,c in enumerate(coeffs_by_loops)]
        #points = [sum(conformBorel(c,1.75,b=b_0+i)) for j,c in enumerate(coeffs_by_loops)]
        print "i = %d, g* = %f, \t"%(i,gStar),points
        #plots.append(plt.plot(L, points, 'o-', label = 'b = %.1f'%(b_0+i)))
        xn, yn = np.array(L),np.array(points, dtype = 'float32')
        x = np.arange(2,10,0.1)
        #popt, pcov = curve_fit(fit_exp, xn, yn)
        #print "approximation: %f*exp(-%f*(x+(%f))) + %f"%(popt[0],popt[1],popt[3],popt[2])
        #plt.plot(x, fit_exp(x, *popt), 'r-', label="Fitted Curve")
        plots.append(plt.plot(L, points, 'o-', label = 'g* = %.2f'%(gStar+0.1*i)))
    title = name
    plt.title(title, fontdict = font)
    plt.legend(loc = "upper left")
    plt.text(L[-2], points[0],'g* =%.2f'%gStar, fontdict = font)
    plt.grid(True)
    plt.xticks(L)
    plt.xlabel('Number of loops')
    plt.savefig(fileName)

def plotBeta(beta_half, name, fileName):
    """
    Plot resummed function f(L), where L -- number of loops.
    Syntax: plot(coeffs, g*, title, fileName_to_save)
    """
    font = {'family' : 'serif',
            'color'  : 'darkred',
            'weight' : 'normal',
            'size'   : 16,
            }
    plt.clf()
    n = len(beta_half)

    L = range(2,n-1)
    plots = []
    gStar_by_loops = [findZero(b) for b in [beta_half[:i] for i in range(4,8)]]
    points = gStar_by_loops
    print "L = ",L ,",  points =",points
    xn, yn = np.array(L),np.array(points, dtype = 'float32')
    x = np.arange(2,10,0.1)
    popt_hyp, pcov = curve_fit(fit_hyperbola, xn, yn)
    plt.plot(x, fit_hyperbola(x, *popt_hyp), '--', label="$g(x) = a/(x-x_0)^b +c$")
    plots.append(plt.plot(L, points, 'ro', label = '$g^* = g^*(L)$'))
    title = name
    plt.title(title, fontdict = font)
    plt.legend(loc = "upper right")
    plt.grid(True)
    plt.xticks(L)
    plt.xlabel('Number of loops')
    plt.savefig(fileName)


if __name__ == "__main__":
    #import Vladimirov_et_all_1984, Kleinert_book
    #print "Vladimirov:\teta =", sum(conformBorel(Vladimirov_et_all_1984.eta(1), eps))
    #print "Kleinert:\teta =", sum(conformBorel(Kleinert_book.eta(1), eps))
    #print conformBorel(Kleinert_book.eta(1), eps)
    #print "\nTest (Kleinert 17.16):\teta =", sum(conformBorel([0, 0, 0.0185, 0.0187, -0.0083, 0.0257], eps * 2))

    L2, L4 = 6, 5
    N = 1 # 1, 0 -1
    Z2   = eval(open('Z2.txt').read())
    Z3   = eval(open('Z3.txt').read())
    beta = eval(open('beta_n%d.txt'%N).read())
    eta_g= eval(open('eta_n%d.txt'%N).read())

    beta = map(lambda x: x.n, beta.gSeries.values())
    eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    #beta_half = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    #eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233] = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    #Z2 = [1, 0, -0.0084915370, -0.005323936, -0.002340342, -0.00135597, -0.0003502]
    #Z3 = [1, 1.0, 0.624930113, 0.4470878, 0.1735522, 0.283165]

    beta_half = [b/2 for b in beta[:L4+2]]
    eta_g = eta_g[:L2 + 1]
    gStar = findZero(beta_half)
    print "g* =", gStar

    print "η(g*) =", sum(conformBorel(eta_g, gStar))
    print len(beta_half), "β(g)/2 =", beta_half
    print len(eta_g), "η(g)/2 =", eta_g
    plot(eta_g,beta_half, '$\eta = \eta(L), n = %d$'%N, 'pic_eta_n%d.pdf'%N)
    #plotBeta(beta_half, '$g^* = g^*(L), n = %d$'%n, 'pic_beta_n%d.pdf'%n)


    # FIXME
    """
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
    """
