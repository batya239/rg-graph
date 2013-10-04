#!/bin/bash

PWD=`pwd`
NAME=$1
POINTS=$2
NODES=$3
NITER=$4
DELTA=$5
NODESPPN=$6
DIR=$7
if [ -z "$LIB" ]; then
    LIB=$HOME/lib/pvegas
fi
if [ -z "$SCRIPTDIR" ]; then
   SCRIPTDIR='/home/mkompan/workspace/rg-graph/phi4/graphs'
fi



PNAME=`echo $DIR/$NAME|sed 's/\//\\\\\//g'`
DIRNAMR=`echo $DIR|sed 's/\//\\\\\//g'`
#echo $PNAME

cat $SCRIPTDIR/qsub-integral.tmpl|sed "s/<DIR>/$DIRNAME/"|sed "s/<PROG>/$PNAME/"|sed "s/<POINTS>/$POINTS/"|sed "s/<NODES>/$NODES/"| sed "s/<ITER>/$NITER/"| sed "s/<DELTA>/$DELTA/"| sed "s/<LIB>/$LIB/"| qsub  -N $NAME -l nodes=$NODESPPN  -q long@pbs-tp.hpc.cc.spbu.ru 
#-W group_list=tpcluster
