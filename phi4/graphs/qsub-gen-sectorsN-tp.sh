#!/bin/bash

WORKDIR=~/workspace/rg-graph/phi4/graphs
GRAPH=$1
NAME="${1}_GS"
MODEL=$2
NODESPPN=1
#echo $PNAME

#cat ~/tmp/qsub-integral.tmpl|sed "s/<PROG>/$PNAME/"|sed "s/<POINTS>/$POINTS/"|sed "s/<NODES>/$NODES/"| sed "s/<ITER>/$NITER/"| sed "s/<DELTA>/$DELTA/"
cd $WORKDIR
cat qsub-gen-sectorsN.tmpl|sed "s/<MODEL>/$MODEL/"|sed "s/<GRAPH>/$GRAPH/"| qsub  -N $NAME -l nodes=$NODESPPN -q long@pbs-tp.hpc.cc.spbu.ru  
#-o logs/ -e logs/

