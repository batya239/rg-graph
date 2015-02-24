#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

import numpy as np # inf, exp, array, arange
from scipy.optimize import curve_fit
from uncertSeries import Series
import matplotlib.pyplot as plt
from conform_Borel import conformBorel, findZero

def fit_exp(x, a, b, c):
    return -a*np.exp(b*x) + c

def plot(coeffs, beta_half, name, b_0 = 2, d = 2):
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
    n = len(coeffs)
    L = range(2,n)
    coeffs_by_loops = [coeffs[:k+1] for k in L]
    plots = []

    for i in range(7): ## loop over b: b=b_0+i
        b_local = b_0+0.5*i
        #gStar = 1.88 
        gStar = findZero(beta_half,b_local)
        #points = [sum(conformBorel(c,gStar_by_loops[j],loops = len(c)-1,b=b_0+i)) for j,c in enumerate(coeffs_by_loops)]
        points = [sum(conformBorel(c,gStar,loops = len(c)-1,b=b_local,n=2, dim = d)) for j,c in enumerate(coeffs_by_loops)]
        print "b = %d, g* = %f, \t"%(b_local,gStar),points
        plots.append(plt.plot(L, points, 'o'))#, label = 'b = %d'%(b_0+i)))
        xn, yn = np.array(L),np.array(points, dtype = 'float32')
        x = np.arange(2,20,0.1)
        try:
            popt, pcov = curve_fit(fit_exp, xn, yn, p0=(0.25,-0.25,0.20))
            a,b,c = popt
            print "approximation: %f*exp(-%f*x) + %f"%(a,b,c)
            plt.plot(x, fit_exp(x, *popt), '-', label="$\\eta(x) = %.3f\,e^{%.3f\,x} + %.4f,\ b = %.1f$"%(a,b,c,b_local))
        except RuntimeError:
            print "Error: approximation not found!" 
            exit()
    title = name
    plt.title(title, fontdict = font)
    plt.legend(loc = "lower right")
    # plt.text(L[-2], points[0],'g* =%.2f'%gStar, fontdict = font)
    plt.grid(True)
    plt.xticks(xrange(2,20,2))
    plt.xlabel('Number of loops')
    #plt.show()
    return plt

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
    try:
        popt_exp, pcov = curve_fit(fit_exp, xn, yn, p0=(0.25,-0.25,1.5))
        a,b,c = popt_exp
        plt.plot(x, fit_exp(x, *popt_exp), '-', label="$g(x) = %.1f\,e^{%.2f\,x} + %.3f$"%(a,b,c))
        lineType = 'o'
    except RuntimeError:
        print "Warning: cannot fit beta-function"
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
    d = 3
    b_0 = 5.0
    L2, L4 = 6, 5
    N = 1 #-1, 0, 1
    beta = eval(open('beta_n%d.txt'%N).read())
    eta_g= eval(open('eta_n%d.txt'%N).read())

    beta = map(lambda x: x.n, beta.gSeries.values())
    eta_g= map(lambda x: x.n,eta_g.gSeries.values())
    #beta_half = [0, -1.0, 1.0, -0.71617362, + 0.930764, -1.582398, 3.260219] ## NB: in fact it's beta/2
    #eta_g = [0., 0., 0.033966148, -0.00202253, 0.01139321, -0.0137366, 0.028233]

    ### For d=3, from Nickel, 1978  <-- for Fig.5 in the paper "6 loops"
    beta_half = [0.,-1., 1., -0.4224965707, 0.3510695978, -0.3765268283, 0.49554795, -0.749689] ## d = 3
    eta_g = [0.,0., 0.0109739369, 0.0009142223, 0.0017962229, -0.00065370, 0.00138781, -0.0016977] ## d = 3

    #beta_half = [be/2 for be in beta[:L4+2]]
    gStar = findZero(beta_half,b = b_0)
    print "g* =", gStar

    # eta_g = eta_g[:L2 + 1]
    print "η(g*) =", sum(conformBorel(eta_g, gStar,b=b_0-3,n=2,loops=L2))
    #print "η(g*) =", [sum(conformBorel(eta_g, 1.4,b=0,loops=l)) for l in [1,2,3,4,5,6]]
    #print len(beta_half), "β(g)/2 =", beta_half
    #print len(eta_g), "η(g)/2 =", eta_g
    plt1 = plot(eta_g,beta_half, '$\eta = \eta(n),\ d = %d,\ N = %d$'%(d,N), b_0 = b_0-3, d = d) ## <-- pic_eta_d3_n1.pdf
    #plt1 = plotBeta(beta_half, '$g_* = g_*(n),\ d = %d,\ N = %d$'%(d,N), b_0 = b_0) ## <-- pic_beta_d3_n1.pdf
    #for i in range(4):
    #    plt1 = plotBeta(beta_half, '$g_* = g_*(n),\ d = %d,\ N = %d$'%(d,N), b_0 = b_0 + 0.5*i) ## <-- pic_beta_d3_n1.pdf
    plt1.show()
