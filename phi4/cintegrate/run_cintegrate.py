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

WORKDIR = os.path.expanduser('~')+'/_scratch/ints/'

os.chdir(WORKDIR)

rc = Client()
print rc.ids

#dview = rc[:]
lview = rc.load_balanced_view()
lview.block = True
print lview.apply_sync(getnode)

try:
    diags = [sys.argv[1]]
except IndexError:
    diags = [ d for d in os.listdir('.') if os.path.isfile(d) and 'int' in d ]
commands = []
for d in diags:
    cmd = 'FIESTA3/bin/CIntegrateMP < '+WORKDIR + d + ' > '+d.replace('int', 'out')
    commands += [cmd]

#for cmd in commands:
#    print cmd

lview.map(cubaRun,commands)
#res = map(cubaRun,commands)
#print res

os.chdir(CUR_DIR)
#python get_answer.py $METHOD
#python compare.py $METHOD
