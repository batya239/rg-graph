#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4
import moments
from graphs import Graph
from lines import Line
import roperation
import sympy
import subgraphs
import calculate

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')

g1=Graph(sys.argv[1])


#phi4.reduce=False
name=str(g1.GenerateNickel())
phi4.SetTypes(g1)
g1.FindSubgraphs(phi4)

g1=g1.ReduceSubgraphs(phi4)
g1.FindSubgraphs(phi4)
print g1
subs_toremove=subgraphs.DetectSauseges(g1._subgraphs)
g1.RemoveSubgaphs(subs_toremove)

print "moment index: ", moments.Generic(phi4, g1)

print_moments(g1._moments())
print "subgraphs: ",g1._subgraphs_m

calculate.save(name,g1,phi4)

calculate.compile(name,phi4)

(res,err) = calculate.execute(name, phi4, neps=0)
for i in range(len(res)):
    print i, (res[i],err[i])
