#!/usr/bin/python
# -*- coding:utf8

import sympy
import rggraph_static as rggrf
from phi3 import *
import swiginac

if "-target" in sys.argv:
    target = int(sys.argv[sys.argv.index('-target')+1])
else:
    target = phi3.target

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
greens=phi3.GetGreens()
G2=greens["G2"]
G3=greens["G3"]


Z1=geseries(1+G2,g,eps,target)
Z3=geseries(1-G3,g,eps,target)

print "Z1 = %s\n"%Z1
print "Z3 = %s\n\n-----------------\n"%Z3



Zf=geseries(Z1**0.5,g,eps,target)
Zg=geseries(Z3*(Z1)**(-1.5),g,eps,target)

print "Zf = %s"%Zf
print "Zg = %s"%Zg

print
#print (eps*g*(swiginac.log(Zg)).diff(g)).series(g==0,target+1)
#print

beta = (-(eps*g)/(1+2*g*(swiginac.log(Zg).diff(g)))).series(g==0,target+2)
#print "beta = ", beta

beta1 = geseries(beta,g,eps,target+2)
print
print "beta = ", beta1

gammag = (-(2*eps*g*(swiginac.log(Zg)).diff(g))/(1+2*g*(swiginac.log(Zg)).diff(g))).series(g==0,target+1)

#print
#print "gammag = ", gammag
gammag1 = geseries(1+gammag,g,eps,target+2)-1
#print
#print "gammag = ", gammag1

gammag2 = geseries(1+gammag1,g,eps,target+1)-1
print
print "gammag = ", gammag2
u_lst=[]
for i in range(1,target+1):
    u_tmp=swiginac.symbol("u%s"%i)
    u_lst.append(u_tmp)
def findU(beta,u_lst,g,e,target):
    if target==1:
        u_res=[]
        cur_u=u_lst[0]
        g_sub=cur_u*e
        eq=swiginac.series_to_poly((swiginac.series_to_poly((beta.subs(g==g_sub)/e/e).series(e==0,1))/cur_u).series(cur_u==0,2))==0
        u_res.append(swiginac.lsolve(eq,cur_u))
        return u_res
    else:
        u_res = findU(beta,u_lst,g,e,target-1)
        cur_u = u_lst[target-1]
        g_sub = cur_u*e**(target)
        for i in range(target-1):
            g_sub=g_sub+u_res[i]*e**(i+1)
        eq=swiginac.series_to_poly((swiginac.series_to_poly((beta.subs(g==g_sub)/e/e).series(e==0,target))).series(cur_u==0,2))==0
#        print "target=%s eq=%s"%(target,eq)
#        print g_sub
        u_t=swiginac.lsolve(eq,cur_u)
        u_res.append(swiginac.series_to_poly(u_t.series(e==0,1))-swiginac.series_to_poly(u_t.series(e==0,0)))
#        print u_res
        return u_res    
        
u_res= findU(beta,u_lst,g,eps,target)
print u_res
u_z=0
for i in range(len(u_res)):
    u_z=u_z+u_res[i]*eps**(i+1)


gammaf = (-(2*eps*g*(swiginac.log(Zf)).diff(g))/(1+2*g*(swiginac.log(Zg)).diff(g))).series(g==0,target+1)

#print
#print "gammaf = ", gammaf
gammaf1 = geseries(1+gammaf,g,eps,target+2)-1
#print
#print "gammaf = ", gammaf1

gammaf2 = geseries(1+gammaf1,g,eps,target+1)-1
print
print "gammaf = ", gammaf2

print gammaf2.subs(g==u_z).series(eps==0,target+1)