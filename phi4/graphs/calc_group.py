#!/usr/bin/python
# -*- coding: utf8
import sys
import re

from dummy_model import _phi3,_phi4
from graphs import Graph

def print_moments(_moments):
    if isinstance(_moments.keys()[0],Line):
        print dict([(x.idx(),_moments[x]._string) for x in _moments])
    else:
        print dict([(x,_moments[x]._string) for x in _moments])

phi4=_phi4('dummy')
if len(sys.argv)>3:
    exec('from %s import execute'%sys.argv[3])
    try:
        exec('from %s normalize'%sys.argv[3])
    except:
        pass
else:
    exec('from calculate import execute')
  



#phi4.reduce=False
name=sys.argv[1]
match=re.match('.*loop(\d*).*',name)
nloops=int(match.groups()[0])
print nloops


(res,err) = execute(name, phi4, points=int(sys.argv[2]), neps=phi4.target-nloops, threads=4, calc_delta=0.0000000001)
for i in range(len(res)):
    print i, (res[i],err[i])
if 'normalize' in dir():
    print normalize(g1, (res, err))
