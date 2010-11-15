#!/usr/bin/python
# -*- coding:utf8

import sympy
#import rggraph_static as rggrf
import sys
import swiginac


g=swiginac.symbol('g')
b1=swiginac.symbol('b1')
b2=swiginac.symbol('b2')
b3=swiginac.symbol('b3')
a1=swiginac.symbol('a1')
a2=swiginac.symbol('a2')
a3=swiginac.symbol('a3')
eps=swiginac.symbol('eps')



def geseries(f,g,eps,n):
    L=swiginac.symbol('L_121_')
    a=f.subs(g==L*g).subs(eps==L*eps).series(L==0,n)
    #print "a=%s"%a
    return swiginac.series_to_poly(swiginac.series_to_poly(a).subs(L==1).series(g==0,n+1))


Z2=1+g*b1+g*g*b2+g*g*g*b3
Z3=1+g*a1+g*g*a2+g*g*g*a3


target=3

gamma2 = (-(eps*g*(swiginac.log(Z2)).diff(g))/(1+2*g*(swiginac.log(Z3)-1.5*swiginac.log(Z2)).diff(g))).series(g==0,target+1)
gamma3 = (-(eps*g*(swiginac.log(Z3)).diff(g))/(1+2*g*(swiginac.log(Z3)-1.5*swiginac.log(Z2)).diff(g))).series(g==0,target+1)


gamma2_1 = geseries(1+gamma2,g,eps,target+2)-1
gamma2_2 = geseries(1+gamma2_1,g,eps,target+2)-1

gamma3_1 = geseries(1+gamma3,g,eps,target+2)-1
gamma3_2 = geseries(1+gamma3_1,g,eps,target+2)-1

print " gamma2= ",gamma2_2
print
print
print " gamma3= ",gamma3_2

