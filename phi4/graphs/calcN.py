#!/usr/bin/python
# -*- coding: utf8
import sys
import dummy_model
from graphs import Graph
import sympy


G = sympy.special.gamma_functions.gamma


if len(sys.argv) == 5:
    modelName = sys.argv[4]
    model = eval('dummy_model.%s("dummy")' % modelName)
    points = int(sys.argv[2])
    exec ('from %s import execute' % sys.argv[3])
    try:
        exec ('from %s import normalize' % sys.argv[3])
    except:
        pass
else:
    print "provide method and model"
    sys.exit(1)

g1 = Graph(sys.argv[1])

#phi4.reduce=False
name = str(g1.GenerateNickel())

(res, err) = execute(name, model, points=points, neps=0, threads=4, calc_delta=0.0)
for i in range(len(res)):
    print i, (res[i], err[i])

print model.normalizeN(g1, (res, err))
