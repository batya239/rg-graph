#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

import graphine, graph_state
from uncertainties import ufloat
from uncertSeries import symmetryCoefficient

outFile = 'diagTable.tex'
resFile = 'res_best_6loops.txt'
KR1File = 'KR1_6loops.out'

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
\\usepackage[a4paper,nohead,includefoot,mag=1000,margin=2cm,footskip=1cm,inner=1.7cm]{geometry} \n \
\n \
\\begin{document} \n \
\\pagestyle{empty} \n \
\\begin{longtable}{|c|c|l|l|c|l|}\n \
\\hline\n \
 & diag & $N$(diag) & $KR'$(diag) & sym. coeff. & final\\\\ \n \
\\hline \n"

tail ="\end{longtable}\n \
    \end{document}"

f = open(outFile,'w')
f.write(head)
for i,diag in enumerate(diagList):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag])
    graph = graphine.Graph(graph_state.GraphState.fromStr(diag))
    graphLoopCount = graph.getLoopsCount()
    coeff = -(-2. / 3) ** graphLoopCount * symmetryCoefficient(graph)
    #print symmetryCoefficient(graph), coeff
    f.write("%d & %s & %s & %s & %f & %s \\\\ \n"%(i+1, diag, r.format('S'),
                       kr.format('S'), symmetryCoefficient(graph), (coeff*kr).format('S') ))
    f.write("\\hline \n")
f.write(tail)
f.close()