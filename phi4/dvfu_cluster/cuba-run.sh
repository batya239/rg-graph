#!/bin/bash

CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
METHOD='divonne'
cd $WORKDIR
for d in `ls -d */`
    do
        cd $d
        #scons -f ../SConstruct
        ./cuba.run 2 50000000 1e-5 1e-12 > out_${PWD##*/}_50M_e-5_e-12_$METHOD
        cd ..
    done
cd $CUR_DIR
python get_answer.py $METHOD
#python compare.py
