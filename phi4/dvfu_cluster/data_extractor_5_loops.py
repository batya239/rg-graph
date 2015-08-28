#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine, graph_state, math
from uncertainties import ufloat
from On_analytic import On
from sympy import latex, var, simplify
from fractions import gcd # <-- Greatest common divisor
from os import system

outFile = 'diagTable_5loops.tex'
resFile = 'res_new.txt'
KR1File = 'KR1_6loops_new.out'

# def multiply(ans1, ans2):
#     r1 = ufloat(ans1[0][0],ans1[1][0])
#     r2 = ufloat(ans2[0][0],ans2[1][0])
#     r = r1* r2
#     return (r.n,), (r.s,)


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
for i in res:
    res[i] = ufloat(-res[i][0][0],res[i][1][0])

KR1 = eval(open(KR1File,'r').read())

res["ee11|ee|"] = ufloat(1., 0.)
res["ee11|22|ee|"] = res["ee11|ee|"] * res["ee11|ee|"]
res["ee11|23|e33|e|"] = res["ee11|ee|"] * res["ee12|e22|e|"]
res["ee11|22|33|ee|"] = res["ee11|ee|"] * res["ee11|22|ee|"]
res["ee11|22|33|44|ee|"] = res["ee11|ee|"] * res["ee11|22|33|ee|"]
res["ee11|23|e44|e44||"] = res["ee11|ee|"] * res["ee12|e33|e33||"]
res["ee11|22|34|e44|e|"] = res["ee11|ee|"] * res["ee11|23|e33|e|"]
res["ee11|23|e34|44|e|"] = res["ee11|ee|"] * res["ee12|e23|33|e|"]
res["ee11|23|ee4|444||"] = res["ee11|ee|"] * res["ee12|ee3|333||"]
res["e112|e2|34|e44|e|"] = res["ee12|e22|e|"] * res["ee12|e22|e|"]
res["ee11|23|334|4|ee|"] = res["ee11|ee|"] * res["ee12|223|3|ee|"]
res["ee11|23|344|45|5|ee|"] = res["ee11|ee|"] * res["ee12|233|34|4|ee|"]
res["ee11|23|e45|e45|55||"] = res["ee11|ee|"] * res["ee12|e34|e34|44||"]
res["ee11|22|34|445|5|ee|"] = res["ee11|ee|"] * res["ee11|23|334|4|ee|"]
res["ee11|23|345|45|e5|e|"] = res["ee11|ee|"] * res["ee12|234|34|e4|e|"]
res["ee11|22|34|e55|e55||"] = res["ee11|ee|"] * res["ee11|23|e44|e44||"]
res["ee11|23|445|455|e|e|"] = res["ee11|ee|"] * res["ee12|334|344|e|e|"]
res["ee11|22|33|45|e55|e|"] = res["ee11|ee|"] * res["ee11|22|34|e44|e|"]
res["e112|e2|34|e45|55|e|"] = res["ee12|e22|e|"] * res["ee12|e23|33|e|"]
res["e112|e2|33|45|e55|e|"] = res["ee12|e22|e|"] * res["ee11|23|e33|e|"]
res["ee11|23|ee4|455|55||"] = res["ee11|ee|"] * res["ee12|ee3|344|44||"]
res["ee11|23|e44|555|e5||"] = res["ee11|ee|"] * res["ee12|e33|444|e4||"]
res["ee11|23|445|445||ee|"] = res["ee11|ee|"] * res["ee12|334|334||ee|"]
res["ee12|223|3|45|e55|e|"] = res["ee12|e22|e|"] * res["ee12|223|3|ee|"]
res["ee11|23|334|5|e55|e|"] = res["ee11|ee|"] * res["ee12|223|4|e44|e|"]
res["ee11|22|33|44|55|ee|"] = res["ee11|ee|"] * res["ee11|22|33|44|ee|"]
res["ee11|23|e34|e5|555||"] = res["ee11|ee|"] * res["ee12|e23|e4|444||"]
res["ee11|23|e44|e55|55||"] = res["ee11|ee|"] * res["ee12|e33|e44|44||"]
res["ee11|23|344|55|e5|e|"] = res["ee11|ee|"] * res["ee12|233|44|e4|e|"]
res["ee12|333|345||e55|e|"] = res["ee12|e22|e|"] * res["ee12|ee3|333||"]
res["ee11|22|34|ee5|555||"] = res["ee11|ee|"] * res["ee11|23|ee4|444||"]
res["ee11|22|34|e45|55|e|"] = res["ee11|ee|"] * res["ee11|23|e34|44|e|"]
res["ee11|23|e44|455|5|e|"] = res["ee11|ee|"] * res["ee12|e33|344|4|e|"]
res["ee11|23|444|455||ee|"] = res["ee11|ee|"] * res["ee11|23|ee4|444||"]
res["ee11|23|e45|445|5|e|"] = res["ee11|ee|"] * res["ee12|e34|334|4|e|"]
res["ee11|23|e34|55|e55||"] = res["ee11|ee|"] * res["ee12|e23|44|e44||"]
res["e112|e2|34|e55|e55||"] = res["ee12|e22|e|"] * res["ee12|e33|e33||"]
res["ee11|23|e34|45|55|e|"] = res["ee11|ee|"] * res["ee12|e23|34|44|e|"]
res["ee11|23|334|4|55|ee|"] = res["ee11|ee|"] * res["ee11|23|334|4|ee|"]



diagList = KR1.keys()
diagList.sort()

print "len(diagList) = %d, len(res) = %d, len(KR1) = %d"%(len(diagList), len(res), len(KR1))

title = "\\documentclass[a4paper]{book}\n \
\\usepackage[english]{babel} \n \
\\usepackage[utf8]{inputenc} \n \
\\usepackage{longtable} \n \
\\usepackage[a4paper,nohead,includefoot,mag=1000,margin=1cm,footskip=1cm,inner=0.5cm]{geometry} \n \
\n \
\\begin{document} \n \
\\pagestyle{empty} \n" 

head = ["\\begin{longtable}{|c|l|l|l|c|l|}\n \
\\hline\n \
 & $\gamma$ & $KR'_2$($\gamma$) & $KR'$($\gamma$) & $S(\gamma)$ & $3^{n+1}\\times O_N$\\\\ \n \
\\hline \n", 
"\\begin{longtable}{|c|l|l|l|c|l|}\n \
\\hline\n \
 & $\gamma$ & $KR'_2$($-\partial_{p^2}\gamma$) & $KR'$($\gamma$) & $S(\gamma$) & $3^n\\times O_N/(N+2)$\\\\ \n \
\\hline \n"]

tail ="\\end{document}"

toSort = []
for i,diag in enumerate(diagList):
    graph = graphine.Graph(graph_state.GraphState.from_str(diag.replace("-","|")))
    graphLoopCount = graph.loops_count
    if graphLoopCount > 5:
        continue
    try:
        # r = ufloat(res[diag.replace('|','-')][0][0],res[diag.replace('|','-')][1][0])
        kr = ufloat(KR1[diag])
    except KeyError:
        print("No result for",diag)
        # print KR1[diag]
        raise
        # continue
    C = symmetryCoefficient(graph)
    coeff = -(-2. / 3) ** graphLoopCount * C[0]/C[1]
    toSort.append([abs(kr.n*coeff),diag])

diagList = [d[1] for d in toSort]
__diagList = [[d for d in diagList if d.count('e')==4],[d for d in diagList if d.count('e')==2]]

n = var('n')
f = open(outFile,'w')
f.write(title)

## 4-legged
current_loop_count = 1
f.write(head[0])
for i,diag in enumerate(sorted(__diagList[0],key = lambda x: len(x))):
    # r = ufloat(res[diag.replace('|','-')][0][0],res[diag.replace('|','-')][1][0])
    r = res[diag]
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag.replace("-","|")))
    graphLoopCount = graph.loops_count
    if graphLoopCount > current_loop_count:
        f.write("\\hline \n")
        current_loop_count += 1
    C = symmetryCoefficient(graph)
    if C[0]%C[1] != 0:
        GCD = gcd(C[0],C[1])
        f.write("%d & $%s$ & %s & %s & %d/%d & $%s$ \\\\ \n"%(i+1,diag.replace("-","|"),r.format('S'),
                       kr.format('S'), C[0]/GCD, C[1]/GCD, latex(simplify(3**(graphLoopCount+1)*On(graph,1))).replace('n','N') ))
    else:
        f.write("%d & $%s$ & %s & %s & %d & $%s$  \\\\ \n"%(i+1, diag.replace("-","|"),r.format('S'),
                       kr.format('S'), C[0]/C[1], latex(simplify(3**(graphLoopCount+1)*On(graph,1))).replace('n','N') ))
f.write("\\hline \n")
f.write("\\end{longtable}\n")

## 2-legged
current_loop_count = 2
f.write(head[1])
for i,diag in enumerate(sorted(__diagList[1],key = lambda x: len(x))):
    # r = ufloat(res[diag.replace('|','-')][0][0],res[diag.replace('|','-')][1][0])
    r = res[diag]
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.from_str(diag.replace("-","|")))
    graphLoopCount = graph.loops_count
    if graphLoopCount > current_loop_count:
        f.write("\\hline \n")
        current_loop_count += 1
    C = symmetryCoefficient(graph)
    if C[0] != C[1]:
        GCD = gcd(C[0],C[1])
        f.write("%d & $%s$ & %s & %s & %d/%d & $%s$ \\\\ \n"%(i+1, diag.replace("-","|"),r.format('S'),
                       kr.format('S'), C[0]/GCD, C[1]/GCD, latex(simplify(3**graphLoopCount*On(graph,1)/(n+2))).replace('n','N') ))
    else:
        f.write("%d & $%s$ & %s & %s & 1 & $%s$  \\\\ \n"%(i+1, diag.replace("-","|"),r.format('S'),
                       kr.format('S'), latex(simplify(3**graphLoopCount*On(graph,1)/(n+2))) ))
f.write("\\hline \n")
f.write("\\end{longtable}\n")
f.write(tail)
f.close()

system('rm %s.aux'%outFile[:-3])
system('pdflatex %s'%outFile)
