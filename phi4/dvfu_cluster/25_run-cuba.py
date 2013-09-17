#!/usr/bin/ipython
# encoding: utf8

## Исполняем все cuba-файлы 

## Параметры cuba:
EpsRel = '1e-6'
EpsAbs = '1e-10'
MaxPoints = '10000000'
Method  = 'suave' ## one of: 'vegas', 'suave', 'divonne', 'cuhre'

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

#dview = rc[:]
lview = rc.load_balanced_view()
print lview.apply_sync(getnode)

diags = [ d for d in os.listdir('.') if os.path.isdir(d) ]
commands = []
for d in diags:
    path = os.path.join(WORKDIR,d)
    cmd = ' '.join((path+'/cuba.run', method_num(Method), MaxPoints, EpsRel, EpsAbs, \
                    '>', '_'.join((path+'/out', d, Method, MaxPoints.replace('0000000','0M'), EpsRel, EpsAbs)) \
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
