#!/usr/bin/python
# -*- coding: utf8
import os

import sys
import re

import polynomial
from graphs import Graph
from methods import sd_tools

import subgraphs
from dummy_model import _phi4

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


model = _phi4("dummy")

graphName = sys.argv[1]
method = sys.argv[2]
exec('import %s as methodModule' % method)

method_name = methodModule.method_name

folder = "%s/%s/%s" % (model.workdir, method_name, graphName)

fileName = folder + "/sectors.py"

fileNameC = "%s" % (graphName)

exec(open(fileName).read())

dynamics.method_name = method_name

G = Graph(graphName)

C_ = polynomial.poly(map(lambda x: (1, x), C), c=(-1., 0))
U_ = polynomial.poly(map(lambda x: (1, x), U))
if len(G.ExternalLines()) == 2:
    D_ = polynomial.poly(map(lambda x: (1, x), D), degree=(-model.space_dim / 2 - 1., 0.5), c=Coef)
else:
    D_ = polynomial.poly(map(lambda x: (1, x), D), degree=(-model.space_dim / 2., 0.5), c=Coef)

expr = C_ * D_ * U_
print "C = %s\nD = %s\nU = %s\n" % (C_, D_, U_)

if 'T' in dir():
    T_ = polynomial.poly(map(lambda x: (1, x), T))
    print "T = %s" % T_
    expr = expr * T_
#print expr


variables = expr.getVarsIndexes()
print "variables: ", variables
uVars, aVars = splitUA(variables)
delta_arg = deltaArg(uVars)

neps = model.target - G.NLoops()
if 'introduce' in dir(methodModule):
    introduce = methodModule.introduce
else:
    introduce = False

dynamics.save(model, expr, sectors, fileNameC, neps, statics=True, introduce=introduce)
dynamics.compileCode(model, fileNameC, options=["-lm", "-lpthread", "-lpvegas", "-O2"])

