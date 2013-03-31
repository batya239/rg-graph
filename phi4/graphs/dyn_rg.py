#!/usr/bin/python
# -*- coding: utf8
import os
import re
import utils

__author__ = 'mkompan'

import sympy
import graphine
import graph_state
from dummy_model import _phi4_dyn


def symmetryCoefficient(graph):
    edges = graph.allEdges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = sympy.factorial(len(graph.edges(graph.externalVertex))) / len(graph.toGraphState().sortings)

    for idxE in unique_edges:
        C = C / sympy.factorial(unique_edges[idxE])
    return C


model = _phi4_dyn('dummy')
model.target = 3

methodName = 'simpleSD'


def normalize(graph, result):
    (res_, err_) = result
    nLoops = graph.calculateLoopsCount()
    e = sympy.var('e')
    res = 0.
    err = 0.
    G = sympy.special.gamma_functions.gamma
    for i in range(len(res_)):
        res += (e / 2) ** i * res_[i]
        err += (e / 2) ** i * abs(err_[i])
    res = res * G(1 + nLoops * e / 2.) * G(2 - e / 2.) ** nLoops / 2 ** nLoops
    err = err * G(1 + nLoops * e / 2.) * G(2 - e / 2.) ** nLoops / 2 ** nLoops

    return ([float(i) for i in utils.series_lst(res, e, len(res_) - 1)],
            [float(i) for i in utils.series_lst(err, e, len(res_) - 1)])


os.chdir("%s/%s" % (model.workdir, methodName))
f1 = 0
e, g = sympy.var('e g')
for dirName in os.listdir('.'):
    print dirName
    if re.match('^e.*_$', dirName):
        fileName = "%s/dyn_sectors.py" % dirName
        exec (open(fileName).read())

        graph = graphine.Graph(graph_state.GraphState.fromStr(graphName))
        nLoops = graph.calculateLoopsCount()
        if map(lambda x: str(x.fields), graph.edges(graph.externalVertex)) == ['0A', '0A']:
            sc = symmetryCoefficient(graph)
            res_, err_ = eval(open("%s/result" % dirName).read())
            res, err = normalize(graph, (res_, err_))
            print dirName, res
            for i in range(model.target - nLoops + 1):
                f1 += (-g) ** nLoops * res[i] * e ** i / 2 * sc

print "f1 = ", f1

f3 = 0
gStar = 2 * e / 3 + 0.753085 * e * e
eta = e * e / 54 * (1 + 327 * e / 324)

gamma1 = (2 * f1 / (1 + f3)).series(g, 0, model.target + 1).removeO()
gamma1star = gamma1.subs(g, gStar).series(e, 0, model.target + 1).removeO()

print "gamma1 = ", gamma1
print "gamma1Star = ", gamma1star
print "gamma_lambda = ", (eta - gamma1star).series(e, 0, model.target + 1).removeO()

R = (-1 + gamma1star / eta).series(e, 0, model.target - 1).removeO()
print "R = ", R

