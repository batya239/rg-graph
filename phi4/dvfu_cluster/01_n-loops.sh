#!/bin/bash

## создаём исполняемые файлы cuba.run
## для всех диаграмм в N петлях 
## Нужные петли указываем вот тут: `ls phi4/e?-[12345]*`

CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'

## WARNING: применять с осторожностью:
rm -rf $WORKDIR/e*

cd '../graphs/'
for diag in $(for i  in `ls phi4/e?-[23]*`; do awk '!/S/{print $1}' $i; done)
    do
        python gen_sectorsN.py $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
        python gen_sdN_mpi.py  $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
    done

## Затем вызываем скрипт запуска этих cuba.run-файлов
cd $CUR_DIR
#./cuba-run.sh
