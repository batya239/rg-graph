#!/usr/bin/python

import sympy
sympy.var('e u t')

expr=t*u**(e/2.)*(((1.-u)**(e/2.)*(1.-0.5*u*t))/(1.+0.5*(1.-u)*t*(1.-0.5*u*t))**(3.-e/2.) + (1.-u*t)**(e/2.)*(1.-0.5*u)/(t+0.5*(1.-u*t)*(1.-0.5*u))**(3.-e/2.) )
#sympy.pretty_print(expr)
for i in range(5):
   expr1=expr.subs(e,0)
   print sympy.printing.ccode2(expr1)
   print
   expr=expr.diff(e)/(i+1.)
   
