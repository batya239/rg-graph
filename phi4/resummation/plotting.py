#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

import numpy as np # inf, exp, array, arange
from scipy.optimize import curve_fit
from uncertSeries import Series
import matplotlib.pyplot as plt
from conform_Borel import conformBorel, findZero

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
            'color'  : 'black',
            'weight' : 'normal',
            'size'   : 16,
            }
    # plt.clf()
    b_0 = 0
    n = len(coeffs)
    L = range(2,n)
    coeffs_by_loops = [coeffs[:k+1] for k in L]
    plots = []
    gStar = findZero(beta_half,b=5)

    for i in range(1): ## loop over b: b=b_0+i
        # points = [sum(conformBorel(c,gStar_by_loops[j],loops = len(c)-1,b=b_0+i)) for j,c in enumerate(coeffs_by_loops)]
        points = [sum(conformBorel(c,gStar,loops = len(c)-1,b=b_0+i,n=1)) for j,c in enumerate(coeffs_by_loops)]
        print "i = %d, g* = %f, \t"%(i,gStar),points
        plots.append(plt.plot(L, points, 'o'))#, label = 'b = %d'%(b_0+i)))
        xn, yn = np.array(L),np.array(points, dtype = 'float32')
        x = np.arange(2,20,0.1)
        try:
            popt, pcov = curve_fit(fit_exp, xn, yn)
            a,b,c = popt
            print "approximation: %f*exp(-%f*x) + %f"%(a,b,c)
            plt.plot(x, fit_exp(x, *popt), '-', label="$\\eta(x) = %.3f\,e^{-%.3f\,x} + %.3f,\ b = %d$"%(a,b,c,b_0+i))
        except RuntimeError:
            pass
        # plots.append(plt.plot(L, points, 'o', label = 'b = %.1f'%(b_0+i)))
    title = name
    plt.title(title, fontdict = font)
    plt.legend(loc = "lower right")
    # plt.text(L[-2], points[0],'g* =%.2f'%gStar, fontdict = font)
    plt.grid(True)
    plt.xticks(xrange(2,20,2))
    plt.xlabel('Number of loops')
    plt.show(fileName)

def plotBeta(beta_half, name, b_0):
    """
    Plot resummed function f(L), where L -- number of loops.
    Syntax: plot(coeffs, g*, title, fileName_to_save)
    """
    font = {'family' : 'serif',
            'color'  : 'black',
            'weight' : 'normal',
            'size'   : 16,
            }
    #plt.clf()
    n = len(beta_half)

    L = range(2,n-1)
    plots = []
    if d == 3:
        gStar_by_loops = [findZero(beta, b = b_0) for beta in [beta_half[:i] for i in range(4,9)]]
    elif d == 2:
        gStar_by_loops = [findZero(beta, b = b_0) for beta in [beta_half[:i] for i in range(4,8)]]
    points = gStar_by_loops
    for i,p in enumerate(points):
        if abs(p)< 1e-13:
            points[i] = 0
    print "n = ",L ,",  init   =",beta_half
    print "n = ",L ,",  points =",points
    xn, yn = np.array(L),np.array(points, dtype = 'float32')
    x = np.arange(2,10,0.1)
    #popt_hyp, pcov = curve_fit(fit_hyperbola, xn, yn)
    try:
        popt_exp, pcov = curve_fit(fit_exp, xn, yn)
        #a,b,c,x_0 = popt_hyp
        #plt.plot(x, fit_hyperbola(x, *popt_hyp), '--', label="$g(x) = %.2f/(x-%.2f)^{%.3f} + %.2f$"%(a,x_0,b,c,))
        a,b,c = popt_exp
        plt.plot(x, fit_exp(x, *popt_exp), '-', label="$g(x) = %.1f\,e^{-%.2f\,x} + %.2f$"%(a,b,c))
        lineType = 'o'
    except RuntimeError:
        lineType = 'o-'
    plots.append(plt.plot(L, points, lineType, label = '$g_* = g_*(n),\quad b=%.1f$'%b_0))
    #plots.append(plt.plot(L, points, 'o-', label = '$g^* = g^*(n),\ b = %.1f$'%b_0))
    title = name# + ',   $b = %s$'%b_0
    plt.title(title, fontdict = font)
    plt.legend(loc = "upper right")
    plt.grid(True)
    plt.xticks(L)
    plt.xlabel('Number of loops')
    return plt


if __name__ == "__main__":
    # eps = 0.5  # d = 3
    # eps = 1.0  # d = 2
    d = 2
    b_0 = 4.7
    L2, L4 = 6, 5
    N = 1 #-1, 0, 1
    # Z2   = eval(open('Z2.txt').read())
    # Z3   = eval(open('Z3.txt').read())
    #beta = eval(open('beta_n%d.txt'%N).read())
    #eta_g= eval(open('eta_n%d.txt'%N).read())

    #beta = map(lambda x: x.n, beta.gSeries.values())
    #eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    beta_half = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233]

    ### For d=3, from Nickel, 1978  <-- for Fig.5 in the paper "6 loops"
    #beta_half = [0.,-1., 1., -0.4224965707, 0.3510695978, -0.3765268283, 0.49554795, -0.749689] ## d = 3
    #eta_g = [0.,0., 0.0109739369, 0.0009142223, 0.0017962229, -0.00065370, 0.00138781, -0.0016977] ## d = 3
    #Z2 = [1, 0, -0.0084915370, -0.005323936, -0.002340342, -0.00135597, -0.0003502]
    #Z3 = [1, 1.0, 0.624930113, 0.4470878, 0.1735522, 0.283165]

    #beta_half = [be/2 for be in beta[:L4+2]]
    gStar = findZero(beta_half,b = b_0)
    print "g* =", gStar

    # eta_g = eta_g[:L2 + 1]
    print "η(g*) =", sum(conformBorel(eta_g, gStar,b=b_0,loops=L2))
    #print "η(g*) =", [sum(conformBorel(eta_g, 1.4,b=0,loops=l)) for l in [1,2,3,4,5,6]]
    #print len(beta_half), "β(g)/2 =", beta_half
    #print len(eta_g), "η(g)/2 =", eta_g
    #plt1 = plot(eta_g,beta_half, '$\eta = \eta(n),\ d = %d,\ N = %d$'%(d,N), 'pic_eta_d3_n%d.pdf'%N) ## <-- pic_eta_d3_n1.pdf
    plt1 = plotBeta(beta_half, '$g_* = g_*(n),\ d = %d,\ N = %d$'%(d,N), b_0 = b_0) ## <-- pic_beta_d3_n1.pdf
    plt1.show()
