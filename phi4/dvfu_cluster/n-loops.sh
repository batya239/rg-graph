#!/bin/bash

CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'

## WARNING: применять с осторожностью:
rm -rf $WORKDIR/e*

cd '../graphs/'
for diag in $(for i  in `ls phi4/e?-[1234]*`; do awk '!/S/{print $1}' $i; done)
    do
        python gen_sectorsN.py $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
        python gen_sdN_mpi.py  $diag methods.feynmanSDdotSF_mpi _phi4_d2_s2
    done
cd $WORKDIR
for d in `ls -d */`
    do
        cd $d
        scons -f ../SConstruct
        ./cuba.run 3 100000 1e-4 1e-8 > out_${PWD##*/}_100k_e-4_e-8_cuhre
        cd ..
    done
cd $CUR_DIR
python get_answer.py
