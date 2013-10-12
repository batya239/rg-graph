#!/bin/bash

CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
METHOD='cuhre'
cd $WORKDIR
for d in `ls -d */`
    do
        cd $d
        scons -j 8 -f ../SConstruct
        cd ..
    done
cd $CUR_DIR
#./20_run-cuba.sh