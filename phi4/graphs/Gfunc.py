#!/usr/bin/python
import sympy
gamma= sympy.special.gamma_functions.gamma

e=sympy.var('e')
lambd=1-e

def G_(l1,l2):
   e=sympy.var('e')
   return gamma(l1+l2-lambd-1)*gamma(1+lambd-l1)*gamma(1+lambd-l2)/(gamma(l1)*gamma(l2)*gamma(2+2*lambd-l1-l2))

def G1_(l1,l2):
   return (-G_(l1,l2-1)+G_(l1-1,l2)+G_(l1,l2))/2

def G2_(l1,l2):
   return (-G_(l1,l2-1)-G_(l1-1,l2)+G_(l1,l2))/2


def G(l1,l2):
   e=sympy.var('e')
   return G_(l1,l2)/e/G_(1,1)
def G1(l1,l2):
   e=sympy.var('e')
   return G1_(l1,l2)/e/G_(1,1)

def G2(l1,l2):
   e=sympy.var('e')
   return G2_(l1,l2)/e/G_(1,1)

def S(d):
   return d*sympy.pi**(d/2)/gamma(d/2+1)


def R(R1):
    """
    calculate (1-K) for R' expression (R=(1-K)R')
    """
    e=sympy.var('e')
    return R1-R1.series(e,0,0).removeO()

def K(expr):
    return expr.series(e,0,0).removeO()
