#!/usr/bin/python

import sympy

def S(d):
   return d*sympy.pi**(d/2.)/sympy.gamma(d/2.+1.)

def coef(d,n,MAX_LOOPS):
   res_=1.
   for i in range(n):
       res_=res_*(S(d-i)/S(d))
   terms=[]
   e=sympy.var('e')
   for i in range(MAX_LOOPS+1):
       terms.append(float(res_.subs(e,0)))
       res_=res_.diff(e)/(i+1.)
   res=0
   for i in range(len(terms)):
      res=res+terms[i]*e**i
   return res
       
MAX_LOOPS=6

sympy.var('e k0 k1 k2 a1 a2 a3 k0_ k1_ k2_')

if __name__ == "__main__":
    d=4-e
    file=open()
    
else:
