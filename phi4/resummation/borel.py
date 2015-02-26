#!/usr/bin/python
# -*- coding: utf8

__author__ = "kirienko"

from uncertSeries import Series
from sympy import gamma, binomial
import scipy.integrate as integrate
from math import sqrt
import numpy as np

class resummed(Series):
    def __init__(self,coeffs,dim = 2, b =5, gStar = None):
        self.coeffs = coeffs
        self.dim = dim
        self.B = b
        self.loops = len(self.coeffs)-1
        if gStar:
            self.gStar = gStar
        else:
            self.gStar = self.find_gStar(self)


    def plot_gStar(self):
        """
        Plotting series as a function of number of loops
        @return:
        """
        pass

    def plot_eta(self):
        """
        Plotting series as a function of number of loops
        @return:
        """
        pass

    @staticmethod
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

    @staticmethod
    def fit_exp(x,a,b,c):
        """
        fitting points with exp()
        @return:
        """
        return a*np.exp(b*x) + c

    def conform_Borel(self, eps, n = 1):
        """
        Produces Borel transform with a conformal mapping of z-plane
        @return:
        """
        #def conformBorel(coeffs, eps, b = 2, loops = 6, n = 1, dim = 3):
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
        return [eps**n*U[k]*integrate.quad(self.func, 0., np.inf, args=(a, self.B, k, eps), limit=100)[0] for k in range(L) ]

    def find_gStar(self, gStar = 1.75, delta = 0.01):
        """
        @return: g* for given beta-function expansion over g
        i.e. a solution of Beta(g)=0
        """
        #def findZero(beta_half, gStar = 1.75, delta = 0.01, b = 2):
        _gStar, _b = gStar, self.B
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

if __name__ == "__main__":
    N=1
    d = 3
    b_0 = 5.0
    L2, L4 = 6, 5
    beta = eval(open('beta_n%d.txt'%N).read())
    beta = map(lambda x: x.n, beta.gSeries.values())
    beta_half =  [be/2 for be in beta[:L4+2]]
    print beta_half, type(beta_half[5])
    b = resummed(beta_half, b = b_0)
    print b.find_gStar()
