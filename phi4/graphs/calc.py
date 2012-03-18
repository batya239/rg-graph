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
if len(sys.argv)>3:
    exec('from %s import execute'%sys.argv[3])
    try:
        exec('from %s import normalize'%sys.argv[3])
    except:
        pass
#else:
#    exec('from calculate import execute')
    
g1=Graph(sys.argv[1])



#phi4.reduce=False
name=str(g1.GenerateNickel())


(res,err) = execute(name, phi4, points=int(sys.argv[2]), neps=phi4.target-g1.NLoops(), threads=4, calc_delta=0.0000000001)
for i in range(len(res)):
    print i, (res[i],err[i])
if 'normalize' in dir():
    print normalize(g1, (res, err))
