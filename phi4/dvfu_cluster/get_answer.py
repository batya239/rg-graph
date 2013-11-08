#!/usr/bin/python
# encoding: utf8

## Собираем и консервируем ответ

import os, sys
from uncertainties import ufloat
try:
    method = sys.argv[1]
except IndexError:
    print "Method does not set, used 'cuhre'"
    method = 'cuhre'
dumpFile = 'res_'+method+'.txt'
#inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'
inPath = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/correct'

result = {}
failed = 0

## На баше это выглядело бы лучше...
for dir in os.listdir(inPath):
    if os.path.isdir(os.path.join(inPath,dir)):
        print "\nDiagram:",dir
        files = os.listdir(os.path.join(inPath,dir))
        ans = ufloat(0.,0.)
        for f in files:
            #if 'out' in f and method +'_1M' in f:
            if 'out' in f and method +'_50M' in f:
                fd = open(os.path.join(inPath,dir,f))
                data = fd.readlines()
                fd.close()
                #print data
                if 'RESULT' in data[-1]:
                    print data[-1],
                    res = data[-1].split('\t')
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
