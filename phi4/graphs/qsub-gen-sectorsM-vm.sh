#!/bin/bash

WORKDIR=~/workspace/rg-graph/phi4/graphs
GRAPH=$1
NAME="${1}_GS"
METHOD=$2
NODESPPN=1
#echo $PNAME

#cat ~/tmp/qsub-integral.tmpl|sed "s/<PROG>/$PNAME/"|sed "s/<POINTS>/$POINTS/"|sed "s/<NODES>/$NODES/"| sed "s/<ITER>/$NITER/"| sed "s/<DELTA>/$DELTA/"
cd $WORKDIR
cat qsub-gen-sectorsM.tmpl|sed "s/<GRAPH>/$GRAPH/"|sed "s/<METHOD>/$METHOD/"| qsub  -N $NAME -l nodes=$NODESPPN -q long@pbs-vm.hpc.cc.spbu.ru -W group_list=vcluster 
#-o logs/ -e logs/

