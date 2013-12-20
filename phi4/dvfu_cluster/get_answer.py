#!/usr/bin/python
# encoding: utf8

## Собираем и консервируем ответ

import os, sys
from uncertainties import ufloat

import graphine
import graph_state
import sympy

def symmetryCoefficient(graphstate):
    edges = graphstate.edges
    unique_edges = dict()
    externalLegCount = 0
    for edge in edges:
        if -1 in edge.nodes:
            externalLegCount += 1
        if str(edge) in unique_edges:
            unique_edges[str(edge)] = unique_edges[str(edge)] + 1
        else:
            unique_edges[str(edge)] = 1
    C = sympy.factorial(externalLegCount) / len(graphstate.sortings)
    for idxE in unique_edges:
#        print idxE,unique_edges[idxE]
        C = C / sympy.factorial(unique_edges[idxE])

    return C
# ---- --------------- ----


def sym_coef(diag):
    return symmetryCoefficient(graph_state.GraphState.fromStr(diag))

def nloops(string):
    return graphine.Graph(graph_state.GraphState.fromStr(string)).getLoopsCount()


try:
    method = sys.argv[1]
except IndexError:
    print "Method does not set, used 'cuhre'"
    method = 'cuhre'
#dumpFile = 'res_'+method+'.txt'
dumpFile = 'res_5loops_'+method+'.txt'
#inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'
inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/archive_feynmanSDdotS_mpi'

result = {}
failed = 0

## На баше это выглядело бы лучше...
for dir in os.listdir(inPath):
    if os.path.isdir(os.path.join(inPath,dir)):
        print "Diagram:",dir
        files = os.listdir(os.path.join(inPath,dir))
        ans = ufloat(0.,0.)
        for f in files:
            #if 'out' in f and method +'_1M' in f:
            if 'out' in f and method +'_50M' in f:
                fd = open(os.path.join(inPath,dir,f))
                data = fd.readlines()
                fd.close()
                #print data
                if 'RESULT' in data[-1]:
                    #print data[-1],
                    res = data[-1].split('\t')
                    res = res[1].split('+-')
                    ans += ufloat(float(res[0]),float(res[1]))
                else:
                    print "No result for", f
                    failed += 1
        ans = float(sympy.gamma(nloops(dir))/sym_coef(dir))*ans
        result.update({dir:[[ans.n],[ans.s]]})
        print "finally:", ans
print result
print "Failed:",failed
fd = open(dumpFile,'w')
fd.write(str(result))
fd.close()
