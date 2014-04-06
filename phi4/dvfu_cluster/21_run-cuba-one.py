#!/usr/bin/python
#! encoding=utf8

## Исполняем все cuba-файлы, которые лежат в конкретной папке <diag>,
## вычисления начинаем на узле <start-node> и далее увеличивем на 1
## Запускаем cuba-файлы c <start_cuba_num> по <end_cuba_num>

import os, sys
from string import zfill

def method_num(method):
    if method   == 'vegas': return '0'
    elif method == 'suave': return '1'
    elif method == 'divonne': return '2'
    elif method == 'cuhre': return '3'

if len(sys.argv) is not 5:
    print "usage: ./21_run-cuba-one <diag> <start-node> <start_cuba_num> <end_cuba_num>"
    print "example: ./21_run-cuba-one e112-34-e34-55-55-- 17 00 13"
else:
    diag = sys.argv[1]
    node = int(sys.argv[2])
    start = sys.argv[3]
    finish = sys.argv[4]
    fill = len(start)

curDir = os.getcwd()
print curDir
workdir = '/home/kirienko/work/rg-graph/phi_4_d2_s2/6loops/'
method = 'suave'
os.chdir(os.path.join(workdir,diag))
for i in range(int(start),int(finish)+1):
    num = zfill(i,fill)
    print "ssh to n%s... start cuba__%s.run"%(node,num)
    ## profile 1
    #out = "out_%s_%s_%s_1M_e-6_e-12"%(num,diag,method)
    #print "result will be stored in",out
    #bin_file = os.path.join(workdir,diag,"cuba__%s.run"%num)
    #cmd = "ssh n%d nohup %s 3 1000000 1e-6 1e-12 > %s &"%(node,bin_file,out)
    #os.system(cmd)
    ## profile 2
    out = "out_%s_%s_%s_99M_e-8_e-12"%(num,diag,method)
    print "result will be stored in",out
    bin_file = os.path.join(workdir,diag,"cuba__%s.run"%num)
    cmd = "ssh n%d nohup %s %s 99999999 1e-8 1e-12 > %s &"%(node,bin_file,method_num(method),out)
    os.system(cmd)
    node +=1

os.chdir(curDir)
