#!/usr/bin/python
# encoding: utf8

## Ищем в папке лучший ответ
## (т.е. с мин. абс. погрешностью)

import os, sys
from uncertainties import ufloat
import sympy, graphine, graph_state

def symmetryCoefficient(graphstate):
    # TODO: sym coeff <-- from uncertSeries.py
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
    return symmetryCoefficient(graph_state.GraphState.fromStr(diag.replace('-','|')))

def nloops(string):
    return graphine.Graph(graph_state.GraphState.fromStr(string.replace('-','|'))).getLoopsCount()


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

def eq(u1,u2):
    """
    Returns True if ufloat u1 is equal to u2 within the stated error,
        and False otherwise.
    """
    return abs(u1.n-u2.n) < u1.s + u2.s

def more_accurate(u1,u2):
    """
    For given ufloats u1 and u2:
    1) Check whether u1 == u2 within the error, and if so
    2) Return more accurate result (i.e., the result with the least error) 
    """
    if eq(u1, u2):
        if u1.s <= u2.s:
            return u1
        else:
            return u2
    else:
        print "\t\t",u1.format('S'),"!=",u2.format('S')
        return u1

dumpFile = 'res_best_6loops.txt'
#inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/6loops'
#inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/archive_feynmanSDdotS_mpi'
inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/all_diags_6_5'

result = {}
failed = 0

## Составляем список диаграмм
try:
    dirs = [sys.argv[1]]
except:
    dirs = [dir for dir in os.listdir(inPath) if os.path.isdir(os.path.join(inPath,dir))]
 
for dir in dirs:
        print dir
        files = [f for f in os.listdir(os.path.join(inPath,dir)) if f[:3] == 'out' ]
        ## Разбиваем на группы по номерам
        numList = {}
        for f in files:
            fileInfo = f.split('_')
            num = fileInfo[1]
            
            f = os.path.join(inPath,dir,f)
            lastLine = tail(f)
            if 'RESULT' in lastLine:
                method = fileInfo[3]
                res = lastLine.split('\t')
                res = res[1].split('+-')
                ans = ufloat(float(res[0]),float(res[1]))
                if num not in numList.keys():
                    numList.update({num:[(ans,method)]})
                else:
                    numList.update({fileInfo[1]:numList[num]+[(ans,method)]})
            else:
                print "No result for", f.split('/')[-1]
                failed += 1

        #print numList
        
        ## Выбираем для каждого кусочка лучший результат
        ans = ufloat(0.,0.)
        ans_cuhre, ans_suave = ufloat(0.,0.),ufloat(0.,0.)
        for d in sorted(numList.keys()):
            #minErr = min(map(lambda x: (x[0].s,x[0].n,x[1]),numList[d]))
            #ans += ufloat(minErr[1],minErr[0])
            for rr in numList[d]:
                if rr[1] == 'cuhre':
                    ans_cuhre += rr[0]
                elif rr[1] == 'suave':
                    ans_suave += rr[0]
        print "\tans_cuhre:",(float(sympy.gamma(nloops(dir))/sym_coef(dir))*ans_cuhre).format('S')
        print "\tans_suave:",(float(sympy.gamma(nloops(dir))/sym_coef(dir))*ans_suave).format('S')
        ans = float(sympy.gamma(nloops(dir))/sym_coef(dir))*more_accurate(ans_cuhre,ans_suave)
        # result.update({dir.replace('-','|'):[[ans.n],[ans.s]]})
        result.update({dir.replace('-','|'):[ans.n,ans.s,method]})
        #print  ans
print result
#print "Failed:",failed

with open(dumpFile,'w') as fd:
    fd.write(str(result))
