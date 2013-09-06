#!/usr/bin/ipython
# encoding: utf8

## Исполняем все cuba-файлы 

## Параметры cuba:
EpsRel = '1e-4'
EpsAbs = '1e-8'
MaxPoints = '1e8'
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


import os
from IPython.parallel import Client

CUR_DIR = os.getcwd()
print CUR_DIR

WORKDIR = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'

os.chdir(WORKDIR)

rc = Client(profile='test')
print rc.ids

dview = rc[:]
print dview.apply_sync(getnode)

diags = [ d for d in os.listdir('.') if os.path.isdir(d) ]
commands = []
for d in diags:
    path = os.path.join(WORKDIR,d)
    cmd = ' '.join((path+'/cuba.run', method_num(Method), MaxPoints, EpsRel, EpsAbs, \
                    '>', '_'.join((path+'/out', d, Method, MaxPoints, EpsRel, EpsAbs)) \
                    ))
    commands += [cmd]

#for cmd in commands:
#    print cmd

dview.map_sync(cubaRun,commands)
#res = map(cubaRun,commands)
#print res

os.chdir(CUR_DIR)
#python get_answer.py $METHOD
#python compare.py $METHOD
