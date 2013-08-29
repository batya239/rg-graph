#!/usr/bin/python
# encoding: utf8

## Собираем и консервируем ответ

import os
dumpFile = 'res.txt'
inPath = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'

result = {}

## На баше это выглядело бы лучше...
for dir in os.listdir(inPath):
    if os.path.isdir(os.path.join(inPath,dir)):
        print "Diagram:",dir
        files = os.listdir(os.path.join(inPath,dir))
        for f in files:
            if 'out' in f:
                fd = open(os.path.join(inPath,dir,f))
                data = fd.readlines()
                fd.close()
                print data
                res = data[-1].split('\t')
                ans,est = res[1].split('+-')
                result.update({dir:(float(ans),float(est))})
print result
fd = open(dumpFile,'w')
fd.write(str(result))
fd.close()
