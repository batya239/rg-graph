#!/usr/bin/python
# -*- coding:utf8

import sympy
import rggraph_static as rggrf
import sys
import swiginac

model = None

def usage(progname):
    return "%s -model phi3R [-target N] [-debug]"

if "-model" in sys.argv:
    model_module = sys.argv[sys.argv.index('-model')+1]
    try:
        exec('from %s import *'%model_module)
    except:
        print "Error while importing model!"
        sys.exit(1)
    if model.name not in ['phi3R1']:
        print "This program works for phi3 model ONLY!"
        sys.exit(1)
else:
    print "Usage : %s " %usage(sys.argv[0])
    sys.exit(1)
    
if "-target" in sys.argv:
    target = int(sys.argv[sys.argv.index('-target')+1])
else:
    target = model.target

g=swiginac.symbol('g')
eps=swiginac.symbol('eps')



def geseries(f,g,eps,n):
    L=swiginac.symbol('L_121_')
    a=f.subs(g==L*g).subs(eps==L*eps).series(L==0,n)
    #print "a=%s"%a
    return swiginac.series_to_poly(swiginac.series_to_poly(a).subs(L==1).series(g==0,n+1))


#G2 =  (g*(0.125000347489694 - 0.0893725486373030*eps - 0.166666737855442/eps) + 
#       g**2*(0.286044194049547 - 0.104085578494757*eps - 0.238485108572760/eps + 
#             0.138888984956952/eps**2) + 
#       g**3*(0.669917578268912 - 0.896541635268446/eps - 0.146605021931999/eps**3 + 
#             0.461482011432618/eps**2))
#G3 = (-g*(0.750000353982726 - 0.536233762649774*eps - 1.00000028867187/eps)
#       - g**2*(3.06128503353258 - 0.959657003971711*eps - 2.35416311194034/eps
#                + 1.25000021001422/eps**2) - g**3*(7.81740005363973 - 10.6221807399268/eps 
#                - 1.66666630630782/eps**3 + 5.28690425966290/eps**2))
AA=[0,0,0,0,0]
BB=[0,0,0,0,0]
g_list = model.GraphList()
eee=sympy.var('eps')
for nickel in g_list:
    G = model.LoadGraph(nickel)
    G.WorkDir()
    G.LoadResults('eps')
    if G.green == '2':
#        BB[G.NLoops()]=BB[G.NLoops()]+float(G.sym_coeff)*G.r1_dot_gamma
        BB[G.NLoops()]=BB[G.NLoops()]-float(G.sym_coeff)*G.r1_dot_gamma

    elif G.green == '3':
        AA[G.NLoops()]=AA[G.NLoops()]+float(G.sym_coeff)*G.r1_dot_gamma
#        print nickel, G.sym_coeff, G.r1_dot_gamma

print BB
print AA
A=[0,0,0,0,0]
B=[0,0,0,0,0]

for i in range(1,5):
   A[i]=AA[i]
   B[i]=BB[i]
   for j in range(1,i):
        print i,j,i-j
#        print AA[j], B[i-j]
#        print AA[j]*B[i-j]
#        print
#        print BB[j], B[i-j-1]
#        print BB[j]*B[i-j-1]
        A[i]=A[i]+AA[j]*B[i-j]
        B[i]=B[i]+BB[j]*B[i-j]
   A[i]=A[i].series(eee,0,5)
   B[i]=B[i].series(eee,0,5)

print
for Bi  in B:
   print "B%s="%B.index(Bi),2*Bi
for Ai in A:
   print "A%s="%A.index(Ai),2*Ai

sys.exit(0)
