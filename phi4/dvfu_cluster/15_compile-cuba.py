#!/usr/bin/ipython
# encoding: utf8

## Компилируем подынтегральные выражения 
## в соответствующие cuba__xx.run-файлы.
## Для одной диаграммы может быть много run-файлов
## (в зависимости от числа сеторов).
import os
from IPython.parallel import Client

CUR_DIR = os.getcwd()
#WORKDIR='/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
#WORKDIR='/home/kirienko/work/rg-graph/phi_4_d2_s2/archive_feynmanSDdotS_mpi/'
WORKDIR='/net/n10/data/kirienko/part_1/'

def getnode():
    import platform
    return platform.node()

def compileCuba(dir):
    import os
    from platform import node
    #wd = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
    wd = '/net/n10/data/kirienko/part_1/'
    os.chdir(os.path.join(wd,dir))
    cmd = 'scons -j 3 -f /home/kirienko/rg-graph/phi4/dvfu_cluster/SConstruct > scons_%s_%s.log 2>&1'%(dir,node())
    os.system(cmd)
    os.system("scons -f /home/kirienko/rg-graph/phi4/dvfu_cluster/SConstruct -c cleanObjs")
    #return "%s scheduled at %s" %(dir,node())

os.chdir(WORKDIR)

rc = Client(profile='small') # variants: ssh
print rc.ids

lview = rc.load_balanced_view()
print lview.apply_sync(getnode)

dirs = os.listdir('.')
dirs = [ d for d in dirs if os.path.isdir(d) ]
#dirs = map(lambda x: x.strip(),open('todo.list').readlines())
print "Diags list:"
for d in dirs: print d

#scheduled = lview.map(compileCuba,dirs)
#for s in scheduled: print s
lview.map(compileCuba,dirs)

os.chdir(CUR_DIR)
