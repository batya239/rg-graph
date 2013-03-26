#!/usr/bin/python

import sys
import os
import fnmatch
import re
from graphs import Graph

import cluster.tools
import dummy_model

method = sys.argv[1]
methodName = method.replace("methods.", "")
modelName = sys.argv[2]
model = eval('dummy_model.%s("dummy")' % modelName)
normalize = model.normalizeN


print "{"

os.chdir("%s/%s" % (model.workdir, methodName))

for dir in os.listdir('.'):
    print dir
    if re.match('^e.*-$', dir):
        g = Graph(dir)
        try:
            res__, err__, time__ = cluster.tools.collect_result(cluster.tools.find_bestresult(dir))
            print res__, err__
            res, err = normalize(g, (res__, err__))
        except ValueError:
            res = []
            err = []
            time__ = []
        print '        "%s": [[' % dir,
        for res_ in res:
            print "%s," % res_,

        print "],  [",
        for err_ in err:
            print "%s," % err_,

        print "]],#",
        print method, ",",
        print

              
print "}"
