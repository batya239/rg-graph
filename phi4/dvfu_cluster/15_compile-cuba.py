#!/usr/bin/ipython
# encoding: utf8

## Компилируем подынтегральные выражения 
## в соответствующие cuba__xx.run-файлы.
## Для одной диаграммы может быть много run-файлов
## (в зависимости от числа сеторов).
import os
from IPython.parallel import Client

CUR_DIR = os.getcwd()
WORKDIR='/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'

def getnode():
    import platform
    return platform.node()

def compileCuba(dir):
    import os
    from platform import node
    wd = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
    os.chdir(os.path.join(wd,dir))
    cmd = 'scons -f ../SConstruct > scons_%s_%s.log 2>&1'%(dir,node())
    os.system(cmd)
    #return "%s scheduled at %s" %(dir,node())

os.chdir(WORKDIR)

rc = Client(profile='test')
print rc.ids

lview = rc.load_balanced_view()
print lview.apply_sync(getnode)

dirs = os.listdir('.')
dirs = [ d for d in dirs if os.path.isdir(d) ]
#print dirs

#scheduled = lview.map(compileCuba,dirs)
lview.map(compileCuba,dirs)
#for s in scheduled: print s

os.chdir(CUR_DIR)
