#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine, graph_state, math
from uncertainties import ufloat
from On_analytic import On
from sympy import latex, var, simplify

outFile = 'diagTable_5loops.tex'
# resFile = 'res_best_6loops.txt'
# resFile = 'res_best_6loops.txt'
KR1File = 'KR1_5loops_yura.out'

def symmetryCoefficient(graph):
    edges = graph.edges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = [math.factorial(len(graph.edges(graph.external_vertex))), len(graph.to_graph_state().sortings)]
    for idxE in unique_edges:
        C[1] = C[1]* (math.factorial(unique_edges[idxE]))
    if C[1]%C[0] == 0:
        C[0],C[1] = 1, C[1]/C[0]
    return C
# def NsymmetryCoefficient(graph):
#     C = symmetryCoefficient(graph)
#     return float(C[0])/float(C[1])

res = eval(open(resFile,'r').read())
KR1 = eval(open(KR1File,'r').read())
diagList = map(lambda x: x.split(' ')[0], open('../graphs/phi4/e4-5loop.txt','r').readlines())
diagList.sort()
for i in range(len(diagList)):
    diagList[i] = diagList[i].replace("-","|")

print len(diagList), len(res), len(KR1)
# print diagList[39]
# print res[diagList[39]]
# print KR1[diagList[39]]

head = "\\documentclass[a4paper]{book}\n \
\\usepackage[english,russian]{babel} \n \
\\usepackage[utf8]{inputenc} \n \
\\usepackage{longtable} \n \
\\usepackage[a4paper,nohead,includefoot,mag=1000,margin=1cm,footskip=1cm,inner=0.5cm]{geometry} \n \
\n \
\\begin{document} \n \
\\pagestyle{empty} \n \
\\begin{longtable}{|c|c|l|l|c|l|l|}\n \
\\hline\n \
 & $\gamma_i$ & $KR'$($\gamma_i$) & $S(\gamma_i$) & $3^6\\times O(n)/(n+2)$\\\\ \n \
\\hline \n"

tail ="\end{longtable}\n \
    \end{document}"

toSort = []
for i,diag in enumerate(diagList):
    try:
        r = ufloat(res[diag][0][0],res[diag][1][0])
        kr = ufloat(KR1[diag])
    except KeyError:
        print("No result for",diag)
        continue
    graph = graphine.Graph(graph_state.GraphState.from_str(diag))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0]/C[1]
    toSort.append([abs(kr.n*coeff),diag])
    # toSort.append([kr.n*coeff,diag])

diagList = [d[1] for d in sorted(toSort,reverse=True)]
print diagList

f = open(outFile,'w')
f.write(head)
n = var('n')
for i,diag in enumerate(diagList):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0] / C[1]
    if C[0] != C[1]:
        f.write("%d & %s & %s & %d/%d & $%s$ \\\\ \n"%(i+1, diag,
                       kr.format('S'), C[0], C[1], latex(simplify(3**6*On(graph,1)/(n+2))) ))
    else:
        f.write("%d & %s & %s & 1 & $%s$  \\\\ \n"%(i+1, diag,
                       kr.format('S'), latex(simplify(3**6*On(graph,1)/(n+2))) ))
    f.write("\\hline \n")
f.write(tail)
f.close()
