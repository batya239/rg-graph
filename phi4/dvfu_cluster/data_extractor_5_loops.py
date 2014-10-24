#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine, graph_state, math
from uncertainties import ufloat
from On_analytic import On
from sympy import latex, var, simplify
from fractions import gcd # <-- Greatest common divisor

outFile = 'diagTable_5loops.tex'
resFile = 'phi4_d2_s2-5loop-e4-100M-6loop-e2-1M.py'
KR1File = 'KR1_5loops.out'

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
diagList = KR1.keys()
diagList.sort()

print "len(diagList) = %d, len(res) = %d, len(KR1) = %d"%(len(diagList), len(res), len(KR1))

title = "\\documentclass[a4paper]{book}\n \
\\usepackage[english,russian]{babel} \n \
\\usepackage[utf8]{inputenc} \n \
\\usepackage{longtable} \n \
\\usepackage[a4paper,nohead,includefoot,mag=1000,margin=1cm,footskip=1cm,inner=0.5cm]{geometry} \n \
\n \
\\begin{document} \n \
\\pagestyle{empty} \n" 

head = ["\\begin{longtable}{|c|l|l|c|l|}\n \
\\hline\n \
 & $\gamma_i$ & $KR'$($\gamma_i$) & $S(\gamma_i)$ & $O(n)$\\\\ \n \
\\hline \n", "\\begin{longtable}{|c|l|l|c|l|}\n \
\\hline\n \
 & $\gamma_i$ & $KR'$($\gamma_i$) & $S(\gamma_i$) & $3^l\\times O(n)/(n+2)$\\\\ \n \
\\hline \n"]

tail ="\\end{document}"

toSort = []
for i,diag in enumerate(diagList):
    try:
        r = ufloat(res[diag][0][0],res[diag][1][0])
        kr = ufloat(KR1[diag])
    except KeyError:
        print("No result for",diag)
        continue
    graph = graphine.Graph(graph_state.GraphState.from_str(diag.replace("-","|")))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0]/C[1]
    toSort.append([abs(kr.n*coeff),diag])

diagList = [d[1] for d in toSort]
__diagList = [[d for d in diagList if d.count('e')==4],[d for d in diagList if d.count('e')==2]]

n = var('n')
f = open(outFile,'w')
f.write(title)

## 4-legged
f.write(head[0])
for i,diag in enumerate(sorted(__diagList[0],key = lambda x: len(x))):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag.replace("-","|")))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    if C[0]%C[1] != 0:
        GCD = gcd(C[0],C[1])
        f.write("%d & $%s$ & %s & %d/%d & $%s$ \\\\ \n"%(i+1, diag.replace("-","|"),
                       kr.format('S'), C[0]/GCD, C[1]/GCD, latex(simplify(3**6*On(graph,1))) ))
    else:
        f.write("%d & $%s$ & %s & %d & $%s$  \\\\ \n"%(i+1, diag.replace("-","|"),
                       kr.format('S'), C[0]/C[1], latex(simplify(3**6*On(graph,1))) ))
    f.write("\\hline \n")
f.write("\\end{longtable}\n")

## 2-legged
f.write(head[1])
for i,diag in enumerate(sorted(__diagList[1],key = lambda x: len(x))):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag.replace("-","|")))
    graphLoopCount = graph.loops_count
    C = symmetryCoefficient(graph)
    if C[0] != C[1]:
        GCD = gcd(C[0],C[1])
        f.write("%d & $%s$ & %s & %d/%d & $%s$ \\\\ \n"%(i+1, diag.replace("-","|"),
                       kr.format('S'), C[0]/GCD, C[1]/GCD, latex(simplify(3**graphLoopCount*On(graph,1)/(n+2))) ))
    else:
        f.write("%d & $%s$ & %s & 1 & $%s$  \\\\ \n"%(i+1, diag.replace("-","|"),
                       kr.format('S'), latex(simplify(3**graphLoopCount*On(graph,1)/(n+2))) ))
    f.write("\\hline \n")
f.write("\\end{longtable}\n")
f.write(tail)
f.close()
