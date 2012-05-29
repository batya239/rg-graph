#!/usr/bin/python
import sympy
gamma= sympy.special.gamma_functions.gamma

def G_(l1,l2):
   e=sympy.var('e')
   return gamma(l1+l2+e-2)*gamma(2-e-l1)*gamma(2-e-l2)/(gamma(l1)*gamma(l2)*gamma(4-l1-l2-2*e))


def G(l1,l2):
   e=sympy.var('e')
   return G_(l1,l2)/e/G_(1,1)

def S(d):
   return d*sympy.pi**(d/2)/gamma(d/2+1)


def R(R1):
    """
    calculate (1-K) for R' expression (R=(1-K)R')
    """
    e=sympy.var('e')
    return R1-R1.series(e,0,0).removeO()