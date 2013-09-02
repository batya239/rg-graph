#!/usr/bin/python
# encoding: utf8

# ---- from ch2nickel.py ----
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

## Сравниваю результаты в 5 петлях: мои и Миши

f_mine = open("res_cuhre.txt")
data1 = eval(f_mine.read())
f_mine.close()

f_mkompan = open("phi4_d2_s2-5loop-e4-100M-6loop-e2-1M.py")
data2 = eval(f_mkompan.read())
f_mkompan.close()

for i in data1.keys():
    try:
        delta = abs(data1[i][0]/sym_coef(i) - data2[i][0][0])
        if delta < 1e-3:
            print i,'\t',delta,'\t', data1[i][0]/sym_coef(i),'\t', data2[i][0][0]
    except:
        #pass
        print i

