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

folder = '6loops' ## 'feynmanSDdotSF_mpi','archive_feynmanSDdotS_mpi'
dumpFile = '_'.join(('res',folder,method))+'.txt'
inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/'+folder

result = {}
all_runs, all_done = 0, 0

## На баше это выглядело бы лучше...
for dir in os.listdir(inPath):
    if os.path.isdir(os.path.join(inPath,dir)) and dir[0] is 'e':
        print "Diagram:",dir
        files = os.listdir(os.path.join(inPath,dir))
        ans = ufloat(0.,0.)
        runs, done = 0,0 # счётчик run-файлов и ответов в папке
        for f in files:
            if 'cuba' in f and 'run' in f:
                runs += 1
                all_runs += 1
            #if 'out' in f and method +'_1M' in f:
            if 'out' in f and method +'_50M' in f:
                fd = open(os.path.join(inPath,dir,f))
                data = fd.readlines()
                fd.close()
                #print data
                if 'RESULT' in data[-1]:
                    res = data[-1].split('\t')
                    res = res[1].split('+-')
                    ans += ufloat(float(res[0]),float(res[1]))
                    done += 1
                    all_done += 1
                #else:
                #    print "No result for", f
        ans = float(sympy.gamma(nloops(dir.replace('-','|')))/sym_coef(dir.replace('-','|')))*ans
        result.update({dir:[[ans.n],[ans.s]]})
        print "finally:", ans.format('S')
        print "%d of %d pieces done for %s" %(done, runs, dir)
print result
print "Total progress: %.0f%% (%d of %d)"%(float(all_done)/all_runs*100, all_done, all_runs)
fd = open(dumpFile,'w')
fd.write(str(result))
fd.close()
