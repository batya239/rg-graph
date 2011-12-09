#!/usr/bin/python
# -*- coding: utf8
from dummy_model import _phi3,_phi4
import moments
from graphs import Graph
from lines import Line
import roperation
import sympy
import subgraphs
import calculate
import sys
import roperation
import conserv
import comb

#from sympy.printing.ccode2 import ccode2


phi4=_phi4('dummy')

if len(sys.argv)==3:
    exec('from %s import save, compile, execute'%sys.argv[2])
else:
    exec('from feynman import save,compile, execute')

g1=Graph(sys.argv[1])
name=str(g1.GenerateNickel())
print name
int_edges=g1._internal_edges_dict()
cons = conserv.Conservations(int_edges)
print cons

det_start = [x for x in comb.xUniqueCombinations(int_edges.keys(), g1.NLoops())]

det=list()
for term in det_start:
    valid = True
    for cterm in cons:
        if cterm.issubset(term):
            valid = False
#            print term, cterm
            break
    if valid:
        det.append(term)
print det
res=0

for term in det:
    sterm=1
    for term2 in term:
       ui=sympy.var('u_%s'%term2)
       sterm=sterm*ui
    res+=sterm
print res

#save(name,g1,phi4)

#compile(name,phi4)

#(res,err) = execute(name, phi4, neps=0)
#for i in range(len(res)):
#    print i, (res[i],err[i])

