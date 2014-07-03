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

diags =[]
try:
    if os.path.isdir(sys.argv[1]):
        WORKDIR = sys.argv[1].replace('~',os.path.expanduser('~'))
        diags += [ d for d in os.listdir(WORKDIR) if os.path.isfile(os.path.join(WORKDIR,d)) and 'int' in d ]
    elif os.path.isfile(sys.argv[1]):
        WORKDIR = os.path.dirname(sys.argv[1].replace('~',os.path.expanduser('~')))
        print "WORKDIR:",WORKDIR
        diags = +[sys.argv[1].replace('~',os.path.expanduser('~'))]
    else:
        print "Error: input path is wrong"
        sys.exit()
except IndexError:
    print "Error: input path with <*.inc>-s is not set, nothing to do"
    sys.exit()
print "diagrams:", diags    
os.chdir(WORKDIR)

rc = Client()
print rc.ids

#dview = rc[:]
lview = rc.load_balanced_view()
lview.block = True
#print lview.apply_sync(getnode)

commands = []
for d in diags:
    cmd = 'time FIESTA3/bin/CIntegrateMP < '+os.path.join(WORKDIR,d)+' > '+os.path.join(WORKDIR,d.replace('int','out'))
    commands += [cmd]

lview.map(cubaRun,commands)
#res = map(cubaRun,commands)
#print res

os.chdir(CUR_DIR)
#python get_answer.py $METHOD
#python compare.py $METHOD
