#!/usr/bin/python
# -*- coding: utf8

__author__ = "kirienko"

from uncertSeries import Series
from sympy import gamma, binomial
import scipy.integrate as integrate
from math import sqrt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


class resummed(Series):
    def __init__(self,coeffs,dim = 2, b =5, gStar = None):
        self.coeffs = coeffs
        self.dim = dim
        self.B = b
        self.loops = len(self.coeffs)-1
        self.gStar = gStar or self.find_gStar()


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
        L = range(2,len(self.coeffs))
        # coeffs_by_loops = [self.coeffs[:k+1] for k in L]
        coeffs_by_loops = [resummed(self.coeffs[:k+1],self.dim,self.B) for k in L]
        plots = []

        #gStar = 1.88
        points = [sum(c.conform_Borel(self.gStar)) for j,c in enumerate(coeffs_by_loops)]
        print "b = %d, g* = %f, \t"%(self.B,self.gStar),points
        plots.append(plt.plot(L, points, 'o'))#, label = 'b = %d'%(b_0+i)))
        xn, yn = np.array(L),np.array(points, dtype = 'float32')
        x = np.arange(2,20,0.1)
        try:
            popt, pcov = curve_fit(self.fit_exp, xn, yn, p0=(0.25,-0.25,0.20))
            a,b,c = popt
            print "approximation: %f*exp(-%f*x) + %f"%(a,b,c)
            plt.plot(x, self.fit_exp(x, *popt), '-', label="$\\eta(x) = %.3f\,e^{%.3f\,x} + %.4f,\ b = %.1f$"%(a,b,c,self.B))
        except RuntimeError:
            print "Error: approximation not found!"
            exit()
        title = '$g_* = g_*(n),\ d = %d,\ N = %d$'%(self.dim,N)
        plt.title(title, fontdict = font)
        plt.legend(loc = "lower right")
        # plt.text(L[-2], points[0],'g* =%.2f'%gStar, fontdict = font)
        plt.grid(True)
        plt.xticks(xrange(2,20,2))
        plt.xlabel('Number of loops')
        #plt.show()
        return plt

    def plot_eta(self):
        """
        Plotting series as a function of number of loops
        @return:
        """
        pass

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

    def find_gStar(self, gStar = 1.75, delta = 0.01):
        """
        @return: g* for given beta-function expansion over g
        i.e. a solution of Beta(g)=0
        """
        _gStar = gStar
        #print "β/2 =", beta_half
        for i in range(1000):
            g2 = sum(self.conform_Borel(_gStar + delta, 1))
            g1 = sum(self.conform_Borel(_gStar - delta, 1))
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
    d = 2
    b_0 = 5.0
    L2, L4 = 6, 5
    beta = eval(open('beta_n%d.txt'%N).read())
    beta = map(lambda x: x.n, beta.gSeries.values())
    beta_half =  [be/2 for be in beta[:L4+2]]
    b = resummed(beta_half, b = b_0)
    plt = b.plot_gStar()
    plt.show()