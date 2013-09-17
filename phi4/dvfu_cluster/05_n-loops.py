#!/usr/bin/ipython
# encoding: utf8
n = 3
## создаём подынтегральные выражения
## для всех диаграмм в N петлях 
## Нужные петли указываем вот тут: `ls phi4/e?-[12345]*`

import os, re
from IPython.parallel import Client

def getnode():
    import platform
    return platform.node()

def getDiags(diag):
    import os
    from platform import node
    path = '/home/kirienko/rg-graph/phi4/graphs/'
    #wd ='/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
    cmd1 = 'python '+path+'gen_sectorsN.py '+diag+' methods.feynmanSDdotSF_mpi _phi4_d2_s2'
    cmd2 = 'python '+path+'gen_sdN_mpi.py  '+diag+' methods.feynmanSDdotSF_mpi _phi4_d2_s2'
    #os.system('python '+path+'gen_sectorsN.py '+diag+' methods.feynmanSDdotSF_mpi _phi4_d2_s2')
    #os.system('python '+path+'gen_sdN_mpi.py  '+diag+' methods.feynmanSDdotSF_mpi _phi4_d2_s2')
    os.system(cmd1)
    os.system(cmd2)
    return "%s scheduled at %s" %(diag,node())

#CUR_DIR=`pwd`
CUR_DIR = os.getcwd()
#WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
WORKDIR='/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'

## WARNING: применять с осторожностью:
#rm -rf $WORKDIR/e*
os.system('rm -rf %s/e*'%WORKDIR)

print CUR_DIR
print WORKDIR

#cd '../graphs/'
os.chdir(os.path.join('..','graphs'))
#print os.getcwd()

#for diag in $(for i  in `ls phi4/e?-[12345]*`; do awk '!/S/{print $1}' $i; done)
#    do
#        python gen_sectorsN.py $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
#        python gen_sdN_mpi.py  $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
#    done
#fls = [ f for f in os.listdir('./phi4/') if int(f[3]) <= n ] 
fls = [ f for f in os.listdir('./phi4/') if f[:4] == 'e2-6' ] 
diags = [ ]
for d in [ open('./phi4/'+f).readlines()for f in fls ]:
    diags.extend(d)
diags = [ d.strip().split(' ')[0] for d in diags if d.strip()[-1] != 'S' ]
print diags

rc = Client(profile='test')
print rc.ids

lview = rc.load_balanced_view()
print lview.apply_sync(getnode)
## Затем вызываем скрипт запуска этих cuba.run-файлов

#lview.map(getDiags,diags)
#scheduled = lview.map(getDiags,diags)

## Direct view!
dview = rc[:]
scheduled = dview.map_sync(getDiags,diags)
for s in scheduled: print s
## Возвращаемся обратно
#cd $CUR_DIR
os.chdir(CUR_DIR)
#./cuba-run.sh
