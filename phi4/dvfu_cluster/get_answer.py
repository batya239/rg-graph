#!/usr/bin/python
# encoding: utf8

## Собираем и консервируем ответ

import os, sys
try:
    method = sys.argv[1]
except IndexError:
    print "Method does not set, used 'cuhre'"
    method = 'cuhre'
dumpFile = 'res_'+method+'.txt'
inPath = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'

result = {}
failed = 0

## На баше это выглядело бы лучше...
for dir in os.listdir(inPath):
    if os.path.isdir(os.path.join(inPath,dir)):
        #print "Diagram:",dir
        files = os.listdir(os.path.join(inPath,dir))
        for f in files:
            if 'out' in f and method+'_10M_1e-6_1e-10' in f:
                fd = open(os.path.join(inPath,dir,f))
                data = fd.readlines()
                fd.close()
                #print data
                if 'RESULT' in data[-1]:
                    res = data[-1].split('\t')
                    ans,est = res[1].split('+-')
                    result.update({dir:[[float(ans),],[float(est)]]})
                else:
                    print "No result for", dir
                    failed += 1
print result
print "Failed:",failed
fd = open(dumpFile,'w')
fd.write(str(result))
fd.close()
