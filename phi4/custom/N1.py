#!/usr/bin/python

import sympy

def S(d):
   return d*sympy.pi**(d/2.)/sympy.gamma(d/2.+1.)

#def S_(d):
#   return S(d)/((2*sympy.pi)**d)

def coef(d,n):
   MAX_LOOPS=5
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
       


sympy.var('e k0 k1 k2 a1 a2 a3 k0_ k1_ k2_')

c3=a1*a2+(1-a1**2)**0.5*(1-a2**2)**0.5*a3

expr=k0**(3.-e)*k1**(3.-e)*k2**(3.-e)*(1.-a1**2)**(0.5-e/2.)*(1.-a2**2)**(0.5-e/2.)*(1.-a3**2)**(-e/2.)*((1+k0**2)**(2)*(1+k1**2)*(1+k2**2)*(1+k0**2+k1**2-2*k0*k1*a1)*(1+k1**2+k2**2-2*k1*k2*c3)*(1+k0**2+k2**2-2*k0*k2*a2))**(-1)
expr=(expr.subs(k0,k0_/(1-k0_))*(1-k0_)**(-2)).subs(k0_,k0)
expr=(expr.subs(k1,k1_/(1-k1_))*(1-k1_)**(-2)).subs(k1_,k1)
expr=(expr.subs(k2,k2_/(1-k2_))*(1-k2_)**(-2)).subs(k2_,k2)
#d=4-e
#expr=S(d-2)/S(d)*S(d-1)/S(d)

coef_=0.202642367285 -0.140460985545*e+0.0160073265426*e*e+0.00116321239084*e**3 + 0.000180204557916*e**4 + 3.53141865283e-05*e**5;

print coef_
print coef(4-e,3)


expr=coef_*expr

sympy.pretty_print(expr)


for i in range(2):
   expr1=expr.subs(e,0)
   print "f[%s]=%s;"%(i,sympy.printing.ccode2((expr1)))
   print
   expr=expr.diff(e)/(i+1.)
   
