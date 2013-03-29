#!/usr/bin/python
# -*- coding: utf8


import sys
import re

import graph_state
import polynomial.sd_lib as sd_lib
import polynomial

import subgraphs
from dummy_model import _phi3_dyn, _phi4_dyn

import dynamics


model = _phi4_dyn("phi4_dyn_test")

filename = sys.argv[1]

exec ('import %s as data' % filename[:-3])

print data.graphName
gs = graph_state.GraphState.fromStr(data.graphName)
tVersion = data.tVersion

dG = dynamics.DynGraph(gs)


neps = model.target - dG.NLoops()

(res, err) = dynamics.execute(filename[:-3], model,
                              neps=neps,
                              points=int(sys.argv[2]),
                              threads=4)
                              #calc_delta=0.0000000001))


for i in range(len(res)):
    print i, (res[i], err[i])

# print
# print "-------------------"
# for sector, aOps in data.sectors:
#
#     sectorExpr = [sd_lib.sectorDiagram(expr, sector, delta_arg=delta_arg)]
#
#     for aOp in aOps:
#         sectorExpr = aOp(sectorExpr)
#     sectorExpr = map(lambda x: x.simplify(), sectorExpr)
#     check = dynamics.checkDecomposition(sectorExpr)
#     print sector, check
#     if "bad" in check:
#         print
#         print polynomial.formatter.format(sectorExpr, polynomial.formatter.CPP)
#         print
#
# #    sectorVariables = set(polynomial.formatter.formatVarIndexes(sectorExpr, polynomial.formatter.CPP))
# #    print sectorVariables
#
#
# #



