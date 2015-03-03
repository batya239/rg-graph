#!/usr/bin/python
# -*- coding: utf8

__author__ = "kirienko"

import scipy.integrate as integrate
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import numpy as np
from uncertSeries import Series
from sympy import gamma, binomial
from math import sqrt
from scipy.optimize import curve_fit
from itertools import cycle

class resummed(Series):
    n_curves = 4 ## <-- number of curves to plot
    def __init__(self, coeffs, dim = 2, b =5, gStar = None):
        self.coeffs = coeffs
        self.dim = dim
        self.B = b
        self.loops = len(self.coeffs)-1
        self.gStar = gStar or self.find_gStar()

    values = range(n_curves)
    ## Possible colormaps: http://matplotlib.org/users/colormaps.html
    jet = plt.get_cmap('cool') # good choice: 'cool', 'jet', 'brg'
    cNorm  = colors.Normalize(vmin=0, vmax=values[-1])
    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=jet)
    colors = cycle([scalarMap.to_rgba(i) for i in range(n_curves)])

    def plot_eta(self):
        """
        Plotting series as a function of number of loops
        @return:
        """
        font = {'family' : 'serif',
                'color'  : 'black',
                'weight' : 'normal',
                'size'   : 16,
                }
        L = range(2,len(self.coeffs))
        # print "L =",L
        coeffs_by_loops = [resummed(self.coeffs[:k+1],gStar=self.gStar, dim = self.dim, b = self.B-3) for k in L]

        points = [sum(c.conform_Borel(c.gStar,n=1)) for c in coeffs_by_loops]
        print "b = %d, g* = %f, \t"%(self.B-3,self.gStar),points
        color = self.colors.next()
        plt.plot(L, points, 'o',c = color)#, label = 'b = %d'%(b_0+i)))
        xn, yn = np.array(L),np.array(points, dtype = 'float32')
        x = np.arange(2,20,0.1)
        try:
            popt, pcov = curve_fit(self.fit_exp, xn, yn, p0=(0.25,-0.25,0.20))
            a,b,c = popt
            print "approximation: %f*exp(%f*x) + %f"%(a,b,c)
            plt.plot(x, self.fit_exp(x, *popt), '-', label="$\\eta(x) = %.3f\,e^{%.3f\,x} + %.4f,\ b = %.1f$"%(a,b,c,self.B-3),c = color)
        except RuntimeError:
            print "Error: approximation not found!"
            exit()
        title = '$\eta = \eta(n),\ d = %d,\ N = %d$'%(self.dim,N)
        plt.title(title, fontdict = font)
        plt.legend(loc = "lower right")
        plt.grid(True)
        plt.xticks(xrange(2,20,2))
        plt.xlabel('Number of loops')
        return plt

    def plot_gStar(self):
        """
        Plotting series as a function of number of loops
        @return:
        """
        font = {'family' : 'serif',
            'color'  : 'black',
            'weight' : 'normal',
            'size'   : 16,
            }
        n = len(self.coeffs)

        L = range(2,n-1)
        ## We know different number of terms in different dimensions
        if self.dim == 3:
            gStar_by_loops = [resummed(beta,b=self.B,gStar=1.43,dim=3).find_gStar(gStar=1.43) for beta in [self.coeffs[:i] for i in range(4,9)]]
        elif self.dim == 2:
            gStar_by_loops = [resummed(beta,b=self.B,gStar=1.43,dim=2).find_gStar(gStar=1.75) for beta in [self.coeffs[:i] for i in range(4,8)]]
        for i,p in enumerate(gStar_by_loops):
            if abs(p)< 1e-13:
                gStar_by_loops[i] = 0
        print "dim =",self.dim, "n = ",L ,",  init   =",beta_half
        print "dim =",self.dim, "n = ",L ,",  points =",gStar_by_loops
        xn, yn = np.array(L),np.array(gStar_by_loops, dtype = 'float32')
        x = np.arange(2,10,0.1)
        color = self.colors.next()
        try:
            popt_exp, pcov = curve_fit(self.fit_exp, xn, yn, p0=(0.25,-0.25,1.5))
            a,b,c = popt_exp
            plt.plot(x, self.fit_exp(x, *popt_exp), '-', label="$g(x) = %.1f\,e^{%.2f\,x} + %.3f$"%(a,b,c),c=color)
            lineType = 'o'
        except RuntimeError:
            print "Warning: cannot fit beta-function"
            lineType = 'o-'
        plt.plot(L, gStar_by_loops, lineType, label = '$g_* = g_*(n),\quad b=%.1f$'%self.B,c=color)
        name = '$g_* = g_*(n),\ d = %d,\ N = %d$'%(self.dim,N)
        title = name# + ',   $b = %s$'%b_0
        plt.title(title, fontdict = font)
        plt.legend(loc = "upper right")
        plt.grid(True)
        plt.xticks(L)
        plt.xlabel('Number of loops')
        return plt


    @staticmethod
    def func(t,a,b,k, g):
        """
        Образ Бореля
        @param t:
        @param a: из АВП
        @param b: из АВП + что-то
        @param k: номер члена
        @param g: заряд!
        @return:
        """
        u = (sqrt(1+a*g*t)-1)/(sqrt(1+a*g*t)+1)
        res = t ** b * np.exp(-t) * u ** (k)
        return res

    @staticmethod
    def fit_exp(x,a,b,c):
        """
        fitting points with exp()
        @return:
        """
        return a*np.exp(b*x) + c

    def conform_Borel(self, g, n = 1):
        """
        Produces Borel transform with a conformal mapping of z-plane
        @return:
        """
        A = self.coeffs
        # print "Initial coeffs:", A
        if self.dim is 2:
            a = 0.238659217# -- for d = 2
        elif self.dim is 3:
            a = 0.14777422 # -- for d = 3
        else:
            raise Exception("Dimension must be either 2 or 3")

        nulls = 0 ## <-- количество начальных нулевых коэффициентов
        for i in A:
            if i == 0: nulls += 1
            else: break
        n = n ## <-- какую степень заряда выносить
        L = self.loops + nulls - n - 1
        A = A[n:]

        # print "A =", A, " len(A)=%d, L=%d"%(len(A),L)
        B = [A[k]/gamma(k+self.B+1) for k in range(L)] ## образ Бореля-Лероя
        # print "B =",B, " len(B)=%d, L=%d"%(len(B),L)
        U = [sum([B[m] * (4/a)**m * binomial(k+m-1,k-m) for m in range(L)]) for k in range(L)]
        # print "U =",U, " len(U)=%d, L=%d"%(len(U),L)
        return [g**n*U[k]*integrate.quad(self.func, 0., np.inf, args=(a, self.B, k, g), limit=100)[0] for k in range(L) ]

    def find_gStar(self, gStar = 1.75, delta = 0.005):
        """
        @return: g* for given beta-function expansion over g
        i.e. a solution of Beta(g)=0
        """
        _gStar = gStar
        #print "β/2 =", beta_half
        for i in range(1000):
            g1 = sum(self.conform_Borel(_gStar - delta, 1))
            g2 = sum(self.conform_Borel(_gStar + delta, 1))
            #print "β(%.2f) = %.4f, β(%.2f) = %.4f" % (_gStar - delta, g1, _gStar + delta, g2)
            if abs(g1) > abs(g2):
                _gStar += delta
            else:
                _gStar -= delta
            if g1 * g2 < 0:
                break
        return _gStar

    def __repr__(self):
        return str(self.coeffs)

if __name__ == "__main__":
    N=1
    d = 3
    n_curves = resummed.n_curves # <-- number of curves to plot
    b_0 = 5.0
    L2, L4 = 6, 5
    if d == 3:
        ### For d=3, from Nickel, 1978  <-- for Fig.5 in the paper "6 loops"
        beta_half = [0.,-1., 1., -0.4224965707, 0.3510695978, -0.3765268283, 0.49554795, -0.749689] ## d = 3
        eta_g = [0.,0., 0.0109739369, 0.0009142223, 0.0017962229, -0.00065370, 0.00138781, -0.0016977] ## d = 3
    elif d == 2:
        beta = eval(open('beta_n%d.txt'%N).read())
        beta = map(lambda x: x.n, beta.gSeries.values())
        beta_half =  [be/2 for be in beta[:L4+2]]
        eta_g= eval(open('eta_n%d.txt'%N).read())
        eta_g= map(lambda x: x.n,eta_g.gSeries.values())
        print "eta_g =",eta_g
    else:
        print "d must be either 2 or 3"

    for i in range(n_curves):
        b = resummed(beta_half, b = b_0+0.5*i, dim = d)
        plt = b.plot_gStar()
        # e = resummed(eta_g,gStar=b.gStar, b = b_0+i, dim = d)
        # plt = e.plot_eta()
    plt.show()