#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4

from graphs import Graph


phi4=_phi4('dummy')

if len(sys.argv)==3:
    exec('from %s import save, compile, execute, Prepare'%sys.argv[2])
else:
    print "provide method"
    sys.exit(1)

g1=Graph(sys.argv[1])
name=str(g1.GenerateNickel())
print name

#phi4.reduce=False

Prepare(g1,phi4)

#print g1._cons
shift=4
res=[]
for cons in g1._cons:
   res.append(frozenset([x-shift for x in cons]))
print
print res
#print g1._qi
