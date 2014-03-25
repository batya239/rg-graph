#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

import numpy as np # inf, exp, array, arange
from scipy.optimize import curve_fit
from uncertSeries import Series
import matplotlib.pyplot as plt
from conform_Borel import conformBorel, findZero

# eps = 0.5  # d = 3
eps = 1.0  # d = 2

def fit_exp(x, a, b, c):
    #print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a*np.exp(-b*x) + c

def fit_hyperbola(x, a, b, c, x_0):
    #print "a = %f, b = %f, c = %f, x_0 = %f" %(a,b,c, x_0)
    return a/(x-x_0)**b + c

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
        points = [sum(conformBorel(c,gStar_by_loops[j],loops = len(c)-1,b=b_0+i)) for j,c in enumerate(coeffs_by_loops)]
        # points = [sum(conformBorel(c,1.88,loops = len(c)-1,b=b_0+i)) for j,c in enumerate(coeffs_by_loops)]
        print "i = %d, g* = %f, \t"%(i,1.88),points
        plots.append(plt.plot(L, points, 'o-', label = 'b = %.1f'%(b_0+i)))
        xn, yn = np.array(L),np.array(points, dtype = 'float32')
        x = np.arange(2,10,0.1)
        # popt, pcov = curve_fit(fit_exp, xn, yn)
        # print "approximation: %f*exp(-%f*x) + %f"%(popt[0],popt[1],popt[2])
        # plt.plot(x, f1it_exp(x, *popt), 'r-', label="Fitted Curve")
        #plots.append(plt.plot(L, points, 'o-', label = 'g* = %.1f'%(gStar+0.1*i)))
    title = name
    plt.title(title, fontdict = font)
    plt.legend(loc = "upper left")
    # plt.text(L[-2], points[0],'g* =%.2f'%gStar, fontdict = font)
    plt.grid(True)
    plt.xticks(L)
    plt.xlabel('Number of loops')
    plt.show(fileName)

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
    L2, L4 = 6, 5
    N = 1 #-1, 0, 1
    Z2   = eval(open('Z2.txt').read())
    Z3   = eval(open('Z3.txt').read())
    beta = eval(open('beta_n%d.txt'%N).read())
    eta_g= eval(open('eta_n%d.txt'%N).read())

    beta = map(lambda x: x.n, beta.gSeries.values())
    eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    beta_half = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233]

    ### For d=3, from Nickel, 1978
    # beta_half = [0.,-1., 1., -0.4224965707, 0.3510695978, -0.3765268283, 0.49554795, -0.749689] ## d = 3
    # eta_g = [0.,0., 0.0109739369, 0.0009142223, 0.0017962229, -0.00065370, 0.00138781, -0.0016977] ## d = 3
    #Z2 = [1, 0, -0.0084915370, -0.005323936, -0.002340342, -0.00135597, -0.0003502]
    #Z3 = [1, 1.0, 0.624930113, 0.4470878, 0.1735522, 0.283165]

    # beta_half = [b/2 for b in beta[:L4+2]]
    # gStar = findZero(beta_half)
    # print "g* =", gStar

    # eta_g = eta_g[:L2 + 1]
    # print "η(g*) =", sum(conformBorel(eta_g, gStar,b=2,loops=L2))
    # print "η(g*) =", [sum(conformBorel(eta_g, 1.4,b=0,loops=l)) for l in [1,2,3,4,5,6]]
    #print len(beta_half), "β(g)/2 =", beta_half
    #print len(eta_g), "η(g)/2 =", eta_g
    plot(eta_g,beta_half, '$\eta = \eta(L), n = %d$'%N, 'pic_eta_d3_n%d.pdf'%N)
    #plotBeta(beta_half, '$g^* = g^*(L),\quad b=0.$', 'pic_beta_d3_b0.pdf')
