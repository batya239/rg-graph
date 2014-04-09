#!/usr/bin/python
# -*- coding: utf8
__author__ = 'kirienko'

from uncertainties import ufloat

outFile = 'diagTable.tex'
resFile = 'res_best_6loops.txt'
KR1File = 'KR1_6loops.out'

res = eval(open(resFile,'r').read())
KR1 = eval(open(KR1File,'r').read())
diagList = map(lambda x: x.split(' ')[0], open('../graphs/phi4/e2-6loop.txt','r').readlines())
for i in range(len(diagList)):
    diagList[i] = diagList[i].replace("-","|")

print len(diagList), len(res), len(KR1)
print diagList[2]
print res[diagList[2]]
print KR1[diagList[2].replace('-','|')+"::"]

head = "\\documentclass[a4paper]{book}\n \
\\usepackage[english,russian]{babel} \n \
\\usepackage[utf8]{inputenc} \n \
\n \
\\begin{document} \n \
\\pagestyle{empty} \n \
\\begin{tabular}{|c|c|c|c|}\n \
\\hline\n \
 & diag & $N$(diag) & $KR'$(diag)\\\\ \n \
\\hline \n"

tail ="\end{tabular}\n \
    \end{document}"

f = open(outFile,'w')
f.write(head)
for i,diag in enumerate(diagList):
    r = ufloat(res[diag][0][0],res[diag][1][0])
    kr = ufloat(KR1[diag.replace('-','|')+"::"])
    f.write("%d & %s & %s & %s \\\\ \n"%(i+1, diag, r.format('S'), kr.format('S')))
    f.write("\\hline \n")
f.write(tail)
f.close()