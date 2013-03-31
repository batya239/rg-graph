#!/usr/bin/python
# -*- coding: utf8
import os

import sys
import re

import graph_state
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
methodName = dynamics.method_name

graphName_ = sys.argv[1]
gs = graph_state.GraphState.fromStr(graphName_)
print str(gs)
dG = dynamics.DynGraph(gs)

if len(sys.argv) == 3:
    tVersions = [eval(sys.argv[2])]
else:
    tVersions = dynamics.TVersions(dG)
pwd = os.environ['PWD']

for tVersion_ in tVersions:
    print
    print "tVersion = ", tVersion_
    name = dynamics.Replace("%s_%s" % (gs, tVersion_))
    dirName = '%s/%s/%s/' % (model.workdir, methodName, name)
    os.chdir(pwd)
    fileName = "%s/dyn_sectors.py" % dirName
    exec (open(fileName).read())

    gs = graph_state.GraphState.fromStr(graphName)

    dG = dynamics.DynGraph(gs)
    dG.FindSubgraphs(model)
    subgraphs.RemoveTadpoles(dG)
    Components = dynamics.generateCDET(dG, tVersion, model=model)
    print str(gs), tVersion
    #print "C = %s\nD = %s\nE = %s\nT = %s\n" % tuple(Components)
    C, D, E, T = Components
    #d=4-2*e

    expr = C * D * E * T
    print "C = %s\nD = %s\nE = %s\nT = %s\n" % (C, D, E, T)
    #print expr

    variables = expr.getVarsIndexes()
    print "variables: ", variables
    uVars, aVars = splitUA(variables)
    delta_arg = deltaArg(uVars)

    neps = model.target - dG.NLoops()
    os.chdir(pwd)
    dynamics.save(model, expr, sectors, name, neps)
    dynamics.compileCode(model, name, options=["-lm", "-lpthread", "-lpvegas", "-O2"])

