#!/usr/bin/python
# encoding: utf8

## Ищем в папке лучший ответ
## (т.е. с мин. абс. погрешностью)

import os, sys
from uncertainties import ufloat

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
inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'
#inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/archive_feynmanSDdotS_mpi'

result = {}
failed = 0

## Составляем список диаграмм
dirs = [dir for dir in os.listdir(inPath) if os.path.isdir(os.path.join(inPath,dir))]
 
for dir in dirs:
        print "Diagram:",dir
        files = [f for f in os.listdir(os.path.join(inPath,dir)) if f[:3] == 'out' ]
        ## Разбиваем на группы по номерам
        numList = {}
        for f in files:
            fileInfo = f.split('_')
            ##
            num = fileInfo[1]
            if num not in numList.keys():
                numList.update({num:[f]})
            else:
                numList.update({fileInfo[1]:numList[num]+[f]})
        print numList
        
        for f in files:
            ans = ufloat(0.,0.)
            #method = 'cuhre'
            f = os.path.join(inPath,dir,f)
            lastLine = tail(f)
            #lastLine = get_data(f)
            if 'RESULT' in lastLine:
                res = lastLine.split('\t')
                res = res[1].split('+-')
                ans += ufloat(float(res[0]),float(res[1]))
            else:
                print "No result for", f
                failed += 1
        result.update({dir:[[ans.n],[ans.s]]})
        print "finally:", ans
print result
print "Failed:",failed
fd = open(dumpFile,'w')
fd.write(str(result))
fd.close()

