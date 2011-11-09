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

#from sympy.printing.ccode2 import ccode2

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')

if len(sys.argv)==3:
    exec('from %s import save, compile, execute'%sys.argv[2])
else:
    exec('from feynman import save,compile, execute')

g1=Graph(sys.argv[1])
name=str(g1.GenerateNickel())
print name
phi4.SetTypes(g1)
g1.FindSubgraphs(phi4)

subs_toremove=subgraphs.DetectSauseges(g1._subgraphs)
g1.RemoveSubgaphs(subs_toremove)

subgraphs.RemoveTadpoles(g1)
phi4.checktadpoles=False

print "moment index: ", moments.Generic(phi4, g1, level=10**6)

print_moments(g1._moments())
print "subgraphs: ",g1._subgraphs

roperation.strechMoments(g1, phi4, external_strech=False)
#print_moments(g1._moments())


save(name,g1,phi4)

compile(name,phi4)

(res,err) = execute(name, phi4, neps=0)
for i in range(len(res)):
    print i, (res[i],err[i])
