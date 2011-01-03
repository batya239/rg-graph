#!/usr/bin/python

import sympy
sympy.var('e u t p p1')

B1=0.5*(u*t*(1.-u)*(1.-u*t/2.))/(1.+t/2.*(1.-u)*(1-u*t/2.))
B2=0.5*(u*t*(1.-u*t)*(1.-u/2.))/(1.+0.5*(1.-u*t)*(1-u/2.))
expr=p**(3.-e)*(1.+p**2)**(-4)*u**(e/2.-1.)*(
      (1.-u)**(-1.+e/2.)*((1.+B1*p*p)**(1.-e)-1.-(1.-e)*B1*p*p)/((1.+t/2.*(1.-u)*(1.-u*t/2.))**(2.-e/2.)) + 
      (1-u*t)**(-1+e/2.)*((1+B2*p**2)**(1-e)-1.-(1.-e)*B2*p**2)/((t+0.5*(1.-u*t)*(1-u*0.5))**(2.-e/2.)) 
      )
expr=(expr.subs(p,p1/(1-p1))*(1-p1)**(-2)).subs(p1,p)

#sympy.pretty_print(expr)
for i in range(2):
   expr1=expr.subs(e,0)
   print "f[%s]=%s;"%(i,sympy.printing.ccode2(expr1))
   print
   expr=expr.diff(e)/(i+1.)
   
