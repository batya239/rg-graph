#!/usr/bin/python
# -*- coding: utf8

import sys
import os
import sympy


from dummy_model import _phi4
import utils

phi4=_phi4('dummy')

if len(sys.argv)>=2:
    exec('from %s import result, normalize'%sys.argv[1])
    method=sys.argv[1]
else:
    exec('from calculate import result')
    method=""

resG, err=result(phi4, method)
for G in resG.keys():
    print type(G)
    print "G%s:\n %s \n %s\n\n"%(G, resG[G],  err[G])

g, n, e = sympy.var('g n e')
A=sympy.var('A0 A1 A2 A3 A4 A5 A6 A7')
B=sympy.var('B0 B1 B2 B3 B4 B5 B6 B7')
N=phi4.target
#N=3
f2=0
for i in range(2, N+1):
    f2=f2+B[i]*g**i
f4=0
for i in range(1, N+1):
    f4+=A[i]*g**i
gam2=2*f2/(1+f2)
gam4=2*f4/(1+f2)
  

g2s=utils.series_f(gam2, g, N)
g4s=utils.series_f(gam4, g, N)
print g2s
print g4s

subs=dict()
for i in range(N+1):
    s_a=str(A[i])
    s_b=str(B[i])
    subs_a=0
    subs_b=0
    for j in range(N-i+1):
        vara=sympy.var("%s_%s"%(s_a, j))
        varb=sympy.var("%s_%s"%(s_b, j))
        subs_a+=vara*e**j
        subs_b+=varb*e**j
    subs[A[i]]=subs_a
    subs[B[i]]=subs_b
    
subs_g=0
tofind=[]
for i in range(1, N+1):
    varg=sympy.var('g_%s'%i)
    subs_g+=varg*e**i
    tofind.append(varg)
subs[g]=subs_g

zeros=[]
gGs=g4s-2*g2s
for var in subs:
    gGs=gGs.subs(var, subs[var])
gGs_e=utils.series_lst(gGs+e, e, N)

def solve_linear(expr, var):
    a=expr.diff(var)
    b=expr.subs(var, 0)
    return -b/a

print gGs_e
print
subs_=dict()
gZ=subs[g]
for i in range(1, N+1):
    gvar=sympy.var('g_%s'%i)
    eq=gGs_e[i]
    for sub in subs_:
        eq=eq.subs(sub, subs_[sub])
#    print eq.expand()
    res=sympy.factor(solve_linear(eq.expand(), gvar))
#    print gvar, res
    subs_[gvar]=res
for sub in subs_:
    gZ=gZ.subs(sub, subs_[sub])   
#print
#print gZ

eta=g2s.subs(g, gZ)
for var in subs:
    eta=eta.subs(var, subs[var])
eta_e=utils.series_f(eta, e, N)
print 
print "eta=" , eta_e
    
for i in range(2, N+1):
    bi=utils.series_lst(resG[2][i], e, N-i)
    print bi
    for j in range(N+1-i):
        eta=eta.subs(sympy.var('B%s_%s'%(i, j)), (-1)**(i+1)*bi[j])
        
for i in range(1, N+1):
    ai=utils.series_lst(resG[4][i], e, N-i)
    print ai
    for j in range(N+1-i):
        print i, j
        eta=eta.subs(sympy.var('A%s_%s'%(i, j)), (-1)**(i)*ai[j])
print utils.series_f(eta, e, N)
