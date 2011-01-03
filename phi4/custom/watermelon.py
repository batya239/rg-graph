#!/usr/bin/python

import sympy
sympy.var('e u t')

expr=t*u**(e/2.)*(((1.-u)**(e/2.)*(1.-0.5*u*t))/(1.+0.5*(1.-u)*t*(1.-0.5*u*t))**(3.-e/2.) + (1.-u*t)**(e/2.)*(1.-0.5*u)/(t+0.5*(1.-u*t)*(1.-0.5*u))**(3.-e/2.) )
sympy.pretty_print(expr)
