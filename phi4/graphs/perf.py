#!/usr/bin/python
# -*- coding: utf8
import sys

from dummy_model import _phi3,_phi4
from graphs import Graph
import sympy
import conserv
import comb
import methods.feynman_tools
import subgraphs

#from sympy.printing.ccode2 import ccode2


phi4=_phi4('dummy')

if len(sys.argv)==3:
    exec('from %s import save, compile, execute'%sys.argv[2])
else:
    exec('from feynman import save,compile, execute')

g1=Graph(sys.argv[1])
#name=str(g1.GenerateNickel())
#print name
name=sys.argv[1]

methods.feynman_tools.Prepare(g1, phi4)

#print g1._det_f
print g1._lines 
print g1._qi
print g1._qi2l
eq_grp=g1.GenerateNickel().GetGroupedEdges()
print eq_grp
print g1._eq_grp
print


    




print methods.feynman_tools.remove_strechs(g1._det_f)
print methods.feynman_tools.remove_strechs(g1._cdet)
print
for item in sorted(methods.feynman_tools._adet_as_lst(g1._cons, g1.NLoops())):
    print item
#save(name,g1,phi4)

#compile(name,phi4)

#(res,err) = execute(name, phi4, neps=0)
#for i in range(len(res)):
#    print i, (res[i],err[i])

