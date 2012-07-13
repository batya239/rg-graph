#!/usr/bin/python

import sys
import os
import fnmatch
import re
from graphs import Graph

import cluster.tools
from dummy_model import _phi4



method = sys.argv[1]
phi4=_phi4('dummy')
try:
    exec('from %s import normalize'%method)
except ImportError:
    normalize=lambda x, y: y

if len(sys.argv)>2:
    accuracy=float(sys.argv[2])
else:
    accuracy=None
    
#name = sys.argv[2]
max=phi4.target-1
for dir in os.listdir('.'):
#    print dir
    if re.match('^e.*-$', dir):
        g=Graph(dir)
#        if g.NLoops()<>5:
#           continue
#        if len(g.ExternalLines())<>2:
#           continue
        try:
#            print dir
            f=open('%s/result'%dir,'r')
            res__, err__=eval(f.read())
#            print res__,err__
            res, err= normalize(g, (res__, err__))
        #except ValueError, IOError:
        except IOError:
            res=[]
            err=[]
            time__=[]
        bad=False
        for x in err:
            if accuracy==None or abs(x)>accuracy:
                bad=True
        if bad:
            print '        "%s": ['%dir ,
            for res_ in res:
                print "%s,"%res_,
#            print ","*(max-len(res)),"], # [",
            print "], # [",
            for err_ in err:
                print "%s,"%err_,
#            print ","*(max-len(err)),"],",
            print "],",
            print method, ",",
#            for time_ in time__:
#                print "%s,%s,"%time_,
#            print ","*(max-len(time__)),
            print

              
