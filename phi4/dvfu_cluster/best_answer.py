#!/usr/bin/python
# encoding: utf8

## Ищем в папке лучший ответ
## (т.е. с мин. абс. погрешностью)

import os, sys
from uncertainties import ufloat
import sympy, graphine, graph_state

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


import subprocess
def tail(f, n=1, offset=0):
    """ similar to usual UNIX 'tail'
    source: http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail
    """
    #stdin,stdout = os.popen2("tail -n %d %s"%(n,f))
    l = subprocess.Popen("tail -n %d "%n+f,shell=True,stdout=subprocess.PIPE,close_fds=True).stdout

    lines = l.read()
    #stdin.close()   
    #lines = stdout.readlines(); stdout.close()
    return lines

def getLastLine(fd):
    fd = open(fd,'r')
    data = fd.readlines()
    fd.close()
    try:
        return data[-1]
    except IndexError:
        return ''


dumpFile = 'res_best.txt'
#inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'
inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/archive_feynmanSDdotS_mpi'

result = {}
failed = 0

## Составляем список диаграмм
dirs = [dir for dir in os.listdir(inPath) if os.path.isdir(os.path.join(inPath,dir))]
 
for dir in dirs:
        print dir+" :",
        files = [f for f in os.listdir(os.path.join(inPath,dir)) if f[:3] == 'out' ]
        ## Разбиваем на группы по номерам
        numList = {}
        for f in files:
            fileInfo = f.split('_')
            num = fileInfo[1]
            
            f = os.path.join(inPath,dir,f)
            lastLine = tail(f)
            if 'RESULT' in lastLine:
                res = lastLine.split('\t')
                res = res[1].split('+-')
                ans = ufloat(float(res[0]),float(res[1]))
                if num not in numList.keys():
                    numList.update({num:[ans]})
                else:
                    numList.update({fileInfo[1]:numList[num]+[ans]})
            else:
                print "No result for", f.split('/')[-1]
                failed += 1

        #print numList
        
        ## Выбираем для каждого кусочка лучший результат
        ans = ufloat(0.,0.)
        for d in sorted(numList.keys()):
            minErr = min(map(lambda x: (x.s,x.n),numList[d]))
            ans += ufloat(minErr[1],minErr[0])
        #print ans
        ans = float(sympy.gamma(nloops(dir))/sym_coef(dir))*ans
        result.update({dir:[[ans.n],[ans.s]]})
        print  ans
#print result
print "Failed:",failed
fd = open(dumpFile,'w')
fd.write(str(result))
fd.close()
