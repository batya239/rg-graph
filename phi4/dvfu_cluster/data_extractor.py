#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine, graph_state, math
from uncertainties import ufloat
from On_analytic import On
from sympy import latex

outFile = 'diagTable.tex'
resFile = 'res_best_6loops.txt'
KR1File = 'KR1_6loops.out'

def symmetryCoefficient(graph):
    edges = graph.allEdges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = [math.factorial(len(graph.edges(graph.external_vertex))), len(graph.toGraphState().sortings)]
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
diagList = map(lambda x: x.split(' ')[0], open('../graphs/phi4/e2-6loop.txt','r').readlines())
diagList.sort()
for i in range(len(diagList)):
    diagList[i] = diagList[i].replace("-","|")

print len(diagList), len(res), len(KR1)
print diagList[39]
print res[diagList[39]]
print KR1[diagList[39]]

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
 & diag & $N$(diag) & $KR'$(diag) & sym.c. & final & O(n)\\\\ \n \
\\hline \n"

tail ="\end{longtable}\n \
    \end{document}"

toSort = []
for i,diag in enumerate(diagList):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.fromStr(diag))
    graphLoopCount = graph.getLoopsCount()
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0]/C[1]
    toSort.append([abs(kr.n*coeff),diag])
    # toSort.append([kr.n*coeff,diag])

diagList = [d[1] for d in sorted(toSort,reverse=True)]
print diagList

f = open(outFile,'w')
f.write(head)
for i,diag in enumerate(diagList):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.fromStr(diag))
    graphLoopCount = graph.getLoopsCount()
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0] / C[1]
    if C[0] != C[1]:
        f.write("%d & %s & %s & %s & %d/%d & %s & $%s$ \\\\ \n"%(i+1, diag, r.format('S'),
                       kr.format('S'), C[0], C[1], (coeff*kr).format('S'), latex(On(graph,1))))
    else:
        f.write("%d & %s & %s & %s & 1 & %s & $%s$  \\\\ \n"%(i+1, diag, r.format('S'),
                       kr.format('S'), (coeff*kr).format('S'), latex(On(graph,1)) ))
    f.write("\\hline \n")
f.write(tail)
f.close()