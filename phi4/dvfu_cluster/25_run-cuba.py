#!/usr/bin/ipython
# encoding: utf8

## Исполняем все cuba-файлы 

## Параметры cuba:
EpsRel = '1e-8'
EpsAbs = '1e-12'
MaxPoints = '50000000'
Method  = 'cuhre' ## one of: 'vegas', 'suave', 'divonne', 'cuhre'

def method_num(method):
    if method   == 'vegas': return '0'
    elif method == 'suave': return '1'
    elif method == 'divonne': return '2'
    elif method == 'cuhre': return '3'

def getnode():
    import platform
    return platform.node()

def cubaRun(cmd):
    import os
    os.system(cmd)
    #return 'Processing'+cmd.split('/')[1]+'...'
    #return cmd.split('/')[1]+' @ '+platform.node()


import os, sys
from IPython.parallel import Client

CUR_DIR = os.getcwd()
print CUR_DIR

#WORKDIR = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
#WORKDIR = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/todo/'
WORKDIR = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/6loops/part_1/'
#WORKDIR = os.path.expanduser('~')+'/work/rg-graph/phi_4_d2_s2/archive_feynmanSDdotS_mpi/'
#WORKDIR = '/net/n15/data/kirienko/'

os.chdir(WORKDIR)

rc = Client(profile='small')
print rc.ids

#dview = rc[:]
lview = rc.load_balanced_view()
print lview.apply_sync(getnode)

try:
    diags = [sys.argv[1]]
except IndexError:
    diags = [ d for d in os.listdir('.') if os.path.isdir(d) ]
commands = []
for d in diags:
    path = os.path.join(WORKDIR,d)
    cubaExecs = [ e for e in os.listdir(path) if '.run' in e ] 
    for e in cubaExecs:
        try:
            execNum = e.split('.')[0].split('__')[1] ##  number of executable
        except IndexError:
            execNum = '0'
        cmd = ' '.join((os.path.join(path,e), method_num(Method), MaxPoints, EpsRel, EpsAbs, \
                    '>', '_'.join((path+'/out', execNum, d, Method, \
                    MaxPoints.replace('0000000','0M'), \
                    EpsRel, EpsAbs)) \
                    ))
        commands += [cmd]

#for cmd in commands:
#    print cmd

lview.map(cubaRun,commands)
#res = map(cubaRun,commands)
#print res

os.chdir(CUR_DIR)
#python get_answer.py $METHOD
#python compare.py $METHOD
