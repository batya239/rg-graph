#!/usr/bin/python
# -*- coding: utf8
import os

import sys
import re

import polynomial
from graphs import Graph
from methods import sd_tools

import subgraphs
import dummy_model

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

if len(sys.argv) == 4:
    modelName = sys.argv[3]
    model = eval('dummy_model.%s("dummy")' % modelName)
    graphName = sys.argv[1]
    method = sys.argv[2]
else:
    print "provide method and model"
    sys.exit(1)


exec('import %s as methodModule' % method)

method_name = methodModule.method_name

folder = "%s/%s/%s" % (model.workdir, method_name, graphName)

fileName = folder + "/sectors.py"

fileNameC = "%s" % graphName

sectorsFileContent = open(fileName).readlines()

exec("\n".join(sectorsFileContent))

dynamics.method_name = method_name

G = Graph(graphName)

C_ = polynomial.poly(map(lambda x: (1, x), C), c=(-1., 0))
U_ = polynomial.poly(map(lambda x: (1, x), U))
if len(G.ExternalLines()) == 2:
    D_ = polynomial.poly(map(lambda x: (1, x), D), degree=(-model.space_dim / 2 - 1., 0), c=Coef)
else:
    D_ = polynomial.poly(map(lambda x: (1, x), D), degree=(-model.space_dim / 2., 0), c=Coef)

expr = C_ * D_ * U_
print "C = %s\nD = %s\nU = %s\n" % (C_, D_, U_)
#print expr


variables = expr.getVarsIndexes()
print "variables: ", variables
uVars, aVars = splitUA(variables)
delta_arg = deltaArg(uVars)

neps = 0

dynamics.save(model, expr, sectors, fileNameC, neps, statics=True)
dynamics.compileCode(model, fileNameC, options=["-lm", "-lpthread", "-lpvegas", "-O2"])

