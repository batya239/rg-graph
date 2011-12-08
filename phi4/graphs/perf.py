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


phi4=_phi4('dummy')

if len(sys.argv)==3:
    exec('from %s import save, compile, execute'%sys.argv[2])
else:
    exec('from feynman import save,compile, execute')

g1=Graph(sys.argv[1])
name=str(g1.GenerateNickel())
print name
print g1._edges()
print type(g1._lines[0])


#save(name,g1,phi4)

#compile(name,phi4)

#(res,err) = execute(name, phi4, neps=0)
#for i in range(len(res)):
#    print i, (res[i],err[i])
