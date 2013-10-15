#!/bin/bash

## Исполняем все cuba-файлы 

CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
METHOD='cuhre'
cd $WORKDIR
for d in `ls -d */`
    do
        cd $d
        for c in `ls cuba__?.run`
            do
                ./$c 3 100000 1e-5 1e-12 > out_${PWD##*/}_10M_e-5_e-12_$METHOD
            done
        cd ..
    done
cd $CUR_DIR
#python get_answer.py $METHOD
#python compare.py $METHOD
