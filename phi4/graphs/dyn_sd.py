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


def splitUA(varSet):
    u = list()
    a = list()
    for var in varSet:
        if isinstance(var, str) and re.match('^a.*', var):
            a.append(var)
        else:
            u.append(var)
    return set(u), set(a)


def deltaArg(varSet):
    return polynomial.poly(map(lambda x: (1, [x]), varSet))




model = _phi4_dyn("phi4_dyn_test")

filename = sys.argv[1]

exec ('import %s as data' % filename[:-3])

gs = graph_state.GraphState.fromStr(data.graphName)
tVersion = data.tVersion

dG = dynamics.DynGraph(gs)
dG.FindSubgraphs(model)
subgraphs.RemoveTadpoles(dG)
Components = dynamics.generateCDET(dG, tVersion)
print str(gs)
print tVersion
print "C = %s\nD = %s\nE = %s\nT = %s\n" % tuple(Components)
C, D, E, T = Components
#d=4-2*e
D.degree.a, D.degree.b = (-model.space_dim / 2., 1)

nLoops = dG.NLoops()
alpha = len([x for x in dG.xInternalLines()])
E.degree.a, E.degree.b = (-alpha + model.space_dim * nLoops / 2. - 1, nLoops)

expr = C * D * E * T
print expr

variables = C.getVarsIndexes()
variables |= D.getVarsIndexes()
variables |= E.getVarsIndexes()
variables |= T.getVarsIndexes()
print "variables: ", variables
uVars, aVars = splitUA(variables)
delta_arg = deltaArg(uVars)


for sector in data.sectors:
    print
    print "-------------------"
    print
    print sector
    sectorExpr = sd_lib.sectorDiagram(expr, sector, delta_arg=delta_arg)
    #some manipulations with sectorExpr

    sectorVariables = set(polynomial.formatter.formatVarIndexes(sectorExpr, polynomial.formatter.CPP))
    print sectorVariables
    print polynomial.formatter.format(sectorExpr, polynomial.formatter.CPP)



