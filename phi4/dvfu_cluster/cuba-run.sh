#!/bin/bash

CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'

cd $WORKDIR
for d in `ls -d */`
    do
        cd $d
        scons -f ../SConstruct
        ./cuba.run 3 10000 1e-4 1e-8 > out_${PWD##*/}_10k_e-4_e-8_cuhre
        cd ..
    done
cd $CUR_DIR
python get_answer.py
