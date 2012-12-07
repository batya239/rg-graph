#!/usr/bin/python
# -*- coding: utf8
import sys
from graphs import Graph
import nickel
from methods import sd_tools
import conserv

import polynomial


def find_eq(cons):
    res = dict()
    eqs = list()
    for tcons in cons:
        if len(tcons) == 2:
            a, b = tuple(tcons)
            new = True
            eqs_ = list()
            for i in range(len(eqs)):
                if a in eqs[i] or b in eqs[i]:
                    eqs[i] = eqs[i] | set([a, b])
                    new = False
                    break
            if new:
                eqs.append(set([a, b]))
    for eq in eqs:
        eq_ = list(eq)
        for var in eq_[1:]:
            res[var] = eq_[0]
    return res


graph = Graph(sys.argv[1])
name = str(graph.GenerateNickel())
if name <> sys.argv[1]:
    raise Exception, "non-minmail Nickel index, minimal index is: %s" % name

graph._eqsubgraphs = list()

internalEdges = graph._internal_edges_dict()
if len(graph.ExternalLines()) == 2:
    internalEdges[1000000] = [i.idx() for i in graph.ExternalNodes()] #Additional edge: suitable way to find F
    conservations = conserv.Conservations(internalEdges)
    equations = find_eq(conservations)
    conservations = sd_tools.apply_eq(conservations, equations)
    graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations, equations)
    graph_ = graph.Clone()
    graph_._cons = conservations
    F = sd_tools.gendet(graph_, N=graph.NLoops() + 1)

    internalEdges = graph._internal_edges_dict()
    conservation = conserv.Conservations(internalEdges)
    conservations = sd_tools.apply_eq(conservations, equations)
    graph._cons = conservations

else:
    F = None

    conservations = conserv.Conservations(internalEdges)
    equations = find_eq(conservations)
    conservations = sd_tools.apply_eq(conservations, equations)
    graph._qi, graph._qi2l = sd_tools.qi_lambda(conservations, equations)
    graph._cons = conservations

U = sd_tools.gendet(graph, N=graph.NLoops())

print "nloops=", graph.NLoops()
print "n=", len(graph._qi2l)

print "Variables : ", ["x%s" % x for x in graph._qi2l]

U_ = [(1, x) for x in U]

print "U=", polynomial.formatter.format(polynomial.poly(U_), polynomial.formatter.CPP)

if F == None:
    F_ = polynomial.poly(U_) * polynomial.poly([(1, [x, ]) for x in graph._qi2l])
else:
    F_ = polynomial.poly([(1, x) for x in F])
print "\n\nF=", polynomial.formatter.format(F_, polynomial.formatter.CPP)

