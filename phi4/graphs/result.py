#!/usr/bin/python
# -*- coding: utf8

from dummy_model import _phi4
import sys
from graphs import Graph
import subgraphs
import os
import sympy

phi4=_phi4('dummy')

if len(sys.argv)>2:
    exec('from %s import result, normalize'%sys.argv[1])
    method=sys.argv[1]
else:
    exec('from calculate import result')
    method=""
    
res, err=result(phi4, method)
for G in res.keys():
    print "G%s:\n %s \n %s\n\n"%(G, res[G],  err[G])
#G2=dict()
#G2_err=dict()
#G4=dict()
#G4_err=dict()
#e,g=sympy.var('e g')
#
#os.chdir(phi4.workdir)
#for file in os.listdir('.'):
#    g=Graph(file)
#    nloop=g.NLoops()
#    n_ext=len(g.ExternalLines())
#    f=open("%s/result"%file,'r')
#    res,err=eval(f.read())
#    f.close()
#    if n_ext==2:
#        g_res=G2
#        g_err=G2_err
#    else:
#        g_res=G4
#        g_err=G4_err
#
#
#    if not nloop in g_res:
#        g_res[nloop]=0.
#        g_err[nloop]=0.
#    g_res[nloop]+=reduce(lambda x,y: x+y, [res[x]*e**x for x in range(len(res))])
#    g_err[nloop]+=reduce(lambda x,y: x+y, [err[x]*e**x for x in range(len(err))])

#print G2
#print G2_err
#
#print
#print G4
#print G4_err
    
