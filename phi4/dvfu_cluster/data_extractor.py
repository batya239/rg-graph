#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine, graph_state, math
from uncertainties import ufloat
from On_analytic import On
from sympy import latex, var, simplify
from os import system

outFile = 'diagTable.tex'
resFile = 'res_final.txt'
# resFile = 'res_5best_6cuhre.txt'
KR1File = 'KR1_6loops.out'

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

res = eval(open(resFile,'r').read())
KR1 = eval(open(KR1File,'r').read())
diagList = map(lambda x: x.split(' ')[0], open('../graphs/phi4/e2-6loop.txt','r').readlines())
for i in range(len(diagList)):
    diagList[i] = diagList[i].replace("-","|")


head = "\\documentclass[a4paper]{book}\n \
\\usepackage[english]{babel} \n \
\\usepackage[utf8]{inputenc} \n \
\\usepackage{longtable} \n \
\\usepackage[a4paper,nohead,includefoot,mag=1000,margin=1cm,footskip=1cm,inner=0.5cm]{geometry} \n \
\n \
\\begin{document} \n \
\\pagestyle{empty} \n \
\\begin{longtable}{|c|c|l|l|c|l|}\n \
\\hline\n \
 & $\gamma$ & $KR'_2(-\partial_{p^2}\gamma$) & $KR'(\gamma)$ & $Sym(\gamma)$ & $3^6\\times O_N/(N+2)$\\\\ \n \
\\hline \n"

tail ="\end{longtable}\n \
    \end{document}"

toSort = []
## Sorting by contribution into the answer
"""
for i,diag in enumerate(diagList):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0]/C[1]
    toSort.append([abs(kr.n*coeff),diag])
"""
## Sorting alphabetically ('e' == 0)
for i,diag in enumerate(diagList):
    toSort.append([diag.replace('|','').replace('e','0'),diag])

diagList = [d[1] for d in sorted(toSort)]
print diagList

f = open(outFile,'w')
f.write(head)
n = var('n')
for i,diag in enumerate(diagList):
    r = ufloat(-res[diag][0],res[diag][1])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0] / C[1]
    if C[0] != C[1]:
       f.write("%d & $%s$ & %s & %s & %d/%d & $%s$ \\\\ \n"%(i+1, diag,
                      r.format('S'), kr.format('S'), C[0], C[1], latex(simplify(3**6*On(graph,1)/(n+2))).replace('n','N') ))
    else:
        f.write("%d & $%s$ & %s & %s & 1 & $%s$  \\\\ \n"%(i+1, diag,
                      r.format('S'), kr.format('S'), latex(simplify(3**6*On(graph,1)/(n+2))).replace('n','N') ))
  
f.write("\\hline \n")
f.write(tail)
f.close()

system('rm %s.aux'%outFile[:-3])
system('pdflatex %s'%outFile)
