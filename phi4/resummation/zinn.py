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

def fit_exp(x, a, b, c):
    #print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a*np.exp(-b*x) + c

def fit_hyperbola(x, a, b, c, x_0):
    #print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a/(x-x_0)**b + c

def conformBorel(coeffs, eps, b = 0.0, loops = 5):
    #if len(coeffs)<=2:
    #    return coeffs
    A = coeffs
    n = 0 ## <-- какую степень заряда выносить
    A = A[n:]

    #a, b = 0.238659217, b # -- for d = 2
    a, b = 0.14777422, b # -- for d = 3
    #B = [A[k]/gamma(k+b+1) for k in range(len(A))] ## образ Бореля-Лероя
    #U = [B[0]] + \
    #    [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(1,k+1)]) for k in range(1,len(B))]
    #print "U =",U
    #return [x*eps**k for k,x in enumerate(A[:4])]+[U[k]*integrate.quad(func, 0., np.inf, args=(a, b, k, eps), limit=100)[0] for k in range(4,len(U)) ]
    ####################
    L=loops+1-n
    #print "A =", A, " len(A)=%d, L=%d"%(len(A),L)
    #B = A[2:]
    B = [A[k]/gamma(k+b+1) for k in range(L)] ## образ Бореля-Лероя
    #print "B =",B
    U = [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(L)]) for k in range(L)]
    #print "U =",U

    #return #[x*eps**(k+n) for k,x in enumerate(A[:2])]+[eps**4*U[k]*integrate.quad(func, 0., np.inf, args=(a, b, k, eps), limit=100)[0] for k in range(2) ]
    return [eps**n*U[k]*integrate.quad(func, 0., np.inf, args=(a, b, k, eps), limit=100)[0] for k in range(L) ]

def findZero(beta_half, gStar = 1.40, delta = 0.01):
    _gStar = gStar
    print "β/2 =", beta_half
    for i in range(1000):
        g1 = sum(conformBorel(beta_half, _gStar - delta,loops = len(beta_half)-1))
        g2 = sum(conformBorel(beta_half, _gStar + delta,loops = len(beta_half)-1))
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
        popt, pcov = curve_fit(fit_exp, xn, yn)
        print "approximation: %f*exp(-%f*(x+(%f))) + %f"%(popt[0],popt[1],popt[3],popt[2])
        plt.plot(x, fit_exp(x, *popt), 'r-', label="Fitted Curve")
        #plots.append(plt.plot(L, points, 'o-', label = 'g* = %.1f'%(gStar+0.1*i)))
    title = name
    plt.title(title, fontdict = font)
    #plt.legend(loc = "upper left")
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
    gStar_by_loops = [findZero(b) for b in [beta_half[:i] for i in range(4,9)]]
    points = gStar_by_loops
    print "L = ",L ,",  points =",points
    xn, yn = np.array(L),np.array(points, dtype = 'float32')
    x = np.arange(2,10,0.1)
    #popt_hyp, pcov = curve_fit(fit_hyperbola, xn, yn)
    #popt_exp, pcov = curve_fit(fit_exp, xn, yn)
    #a,b,c,x_0 = popt_hyp
    #plt.plot(x, fit_hyperbola(x, *popt_hyp), '--', label="$g(x) = %.2f/(x-%.2f)^{%.3f} + %.2f$"%(a,x_0,b,c,))
    #a,b,c = popt_exp
    #plt.plot(x, fit_exp(x, *popt_exp), '--', label="$g(x) = %.2f * e^{-%.2f*x} + %.2f$"%(a,b,c,))
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
    Z2   = eval(open('Z2.txt').read())
    Z3   = eval(open('Z3.txt').read())
    beta = eval(open('beta.txt').read())
    eta_g= eval(open('eta.txt').read())

    beta = map(lambda x: x.n, beta.gSeries.values())
    eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    #beta_half = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    #eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233] = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    ### For d=3, from Nickel, 1978
    beta_half = [0.,-1., 1., -0.4224965707, 0.3510695978, -0.3765268283, 0.49554795, -0.749689]
    eta_g = [0.,0., 0.0109739369, 0.0009142223, 0.0017962229, -0.00065370, 0.00138781, -0.0016977]
    #Z2 = [1, 0, -0.0084915370, -0.005323936, -0.002340342, -0.00135597, -0.0003502]
    #Z3 = [1, 1.0, 0.624930113, 0.4470878, 0.1735522, 0.283165]

    #beta_half = [b/2 for b in beta[:L4+2]]
    #eta_g = eta_g[:L2 + 1]
    #gStar = findZero(beta_half)
    #print "g* =", gStar

    #print "η(g*) =", sum(conformBorel(eta_g, 1.4,b=0,loops=5))
    print "η(g*) =", [sum(conformBorel(eta_g, 1.4,b=0,loops=l)) for l in [1,2,3,4,5,6]]
    #print len(beta_half), "β(g)/2 =", beta_half
    #print len(eta_g), "η(g)/2 =", eta_g
    #plot(eta_g,beta_half, '$\eta = \eta(L)$', 'pic_eta.pdf')
    plotBeta(beta_half, '$g^* = g^*(L),\quad b=0.$', 'pic_beta_d3_b0.pdf')
