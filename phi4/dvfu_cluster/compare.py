#!/usr/bin/python
# encoding: utf8

# ---- from ch2nickel.py ----
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

## Сравниваю результаты в 5 петлях: мои и Миши
import sys
try:
    inFile = sys.argv[1]
except:
    print "Usage: ./compare.py <inFile>\n where \
    <inFile> is file that contains a dict\
    with results\n"
f_mine = open(inFile)
data1 = eval(f_mine.read())
f_mine.close()

f_mkompan = open("phi4_d2_s2-5loop-e4-100M-6loop-e2-1M.py")
data2 = eval(f_mkompan.read())
f_mkompan.close()

okay = 0
print "\tdiagram \t delta \t\t\tmine result \t\t mkompan's result"
for i in data1.keys():
    try:
        #delta = abs(data1[i][0][0]*sympy.gamma(nloops(i))/sym_coef(i) - data2[i][0][0])
        #err_mine = data1[i][1][0]*sympy.gamma(nloops(i))/sym_coef(i)
        delta = abs(data1[i][0][0] - data2[i][0][0])
        err_mine = data1[i][1][0]
        err_mkompan = data2[i][1][0]
        #if delta < max(data1[i][1][0],data2[i][1][0]):#0.99e-6:
        if delta < 0.99e-4:
            #print i,':OK\t',delta,'\t', err_mine,'\t', err_mkompan, '\t', err_mkompan/err_mine
            okay += 1
        else:
            print i,'\t',delta,'\t', data1[i][0][0],'\t', data2[i][0][0]
    except:
        print "Exception:",i

print "OK / total number of diagrams: %d / %d"%(okay,len(data1.keys()))
