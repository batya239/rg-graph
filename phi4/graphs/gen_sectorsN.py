#!/usr/bin/python
# -*- coding: utf8
import sys
import dummy_model

from graphs import Graph


if len(sys.argv) == 4:
    modelName = sys.argv[3]
    model = eval('dummy_model.%s("dummy")' % modelName)
    exec ('from %s import save, compile, execute' % sys.argv[2])
else:
    print "provide method and model"
    sys.exit(1)

g1 = Graph(sys.argv[1])
name = str(g1.GenerateNickel())
print name

#phi4.reduce=False

save(name, g1, model)

#   compile(name,phi4)

#(res,err) = execute(name, phi4, neps=0)
#for i in range(len(res)):
#    print i, (res[i],err[i])

