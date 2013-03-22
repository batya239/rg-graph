#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3, _phi4_d3

from graphs import Graph


phi4 = _phi4_d3('dummy')

if len(sys.argv) == 3:
    exec ('from %s import save, compile, execute' % sys.argv[2])
else:
    print "provide method"
    sys.exit(1)

g1 = Graph(sys.argv[1])
name = str(g1.GenerateNickel())
print name

#phi4.reduce=False

save(name, g1, phi4)

#   compile(name,phi4)

#(res,err) = execute(name, phi4, neps=0)
#for i in range(len(res)):
#    print i, (res[i],err[i])

