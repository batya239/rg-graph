#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4

from graphs import Graph


phi4=_phi4('dummy')

if len(sys.argv)==3:
    exec('from %s import save, compile, execute'%sys.argv[2])
else:
    print "provide method"
    sys.exit(1)

lst=['e123-e23-33--','e112-23-33-e-']
g_lst=map(Graph,lst)

name='g2_loop4_r1_r3'
print name



save(name,g_lst,phi4)

compile(name,phi4)

(res,err) = execute(name, phi4, neps=0)
for i in range(len(res)):
    print i, (res[i],err[i])

