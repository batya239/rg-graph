#!/usr/bin/python
# -*- coding: utf8

__author__ = "kirienko"

class resummed(Series):
    def __init__(self):
        self.dim = dim
        self.gStar = gStar
        self.B = b

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
    def fit_exp(x,a,b,c):
        """
        fitting points with exp()
        @return:
        """
        return a*np.exp(b*x) + c

    def conform_Borel(self):
        """
        Produces Borel transform with a conformal mapping of z-plane
        @return:
        """
        pass

    def find_gStar(self):
        """
        @return: g* for given beta-function expansion over g
        i.e. a solution of Beta(g)=0
        """
        pass

if __name__ == "__main__":
    N=1
    beta = eval(open('beta_n%d.txt'%N).read())
