#!/usr/bin/python

import sympy
sympy.var('e k0 k1 k2 a1 a2 a3')

expr=k0**(3.-e)*k1**(3.-e)*k2**(3.-e)*(1.-a1**2)**(1.-e/2.)*(1.-a2**2)**(1.-e/2.)*(1.-a3**2)**(0.5-e/2.)*((1+k0**2)**(2)*(1+k1**2)*(1+k2**2)*(1+k0**2+k1**2-2*k0*k1*a1)*(1+k1**2+k2**2-2*k1*k2*a3)*(1+k0**2+k2**2-2*k0*k2*a2))**(-1)


for i in range(2):
   expr1=expr.subs(e,0)
   print "f[%s]=%s;"%(i,sympy.printing.ccode2(expr1))
   print
   expr=expr.diff(e)/(i+1.)
   
