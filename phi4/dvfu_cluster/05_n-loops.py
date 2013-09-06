#!/usr/bin/ipython
# encoding: utf8
n = 3
## создаём исполняемые файлы cuba.run
## для всех диаграмм в N петлях 
## Нужные петли указываем вот тут: `ls phi4/e?-[12345]*`

import os, re
from IPython.parallel import Client

#CUR_DIR=`pwd`
CUR_DIR = os.getcwd()
#WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
WORKDIR = '/home/kirienko/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi'

## WARNING: применять с осторожностью:
#rm -rf $WORKDIR/e*
#os.system('rm -rf %s/e*',%WORKDIR)

print CUR_DIR
print WORKDIR

#cd '../graphs/'
os.chdir(os.path.join('..','graphs','phi4'))
print os.getcwd()

#for diag in $(for i  in `ls phi4/e?-[12345]*`; do awk '!/S/{print $1}' $i; done)
#    do
#        python gen_sectorsN.py $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
#        python gen_sdN_mpi.py  $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
#    done
fls = [ f for f in os.listdir('.') if int(f[3]) <= n ] 
for f in fls:
    print open(f).readlines()

## Затем вызываем скрипт запуска этих cuba.run-файлов
#cd $CUR_DIR
os.chdir(CUR_DIR)
#./cuba-run.sh
