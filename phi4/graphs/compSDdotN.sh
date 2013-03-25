#!/bin/sh

PWD=`pwd`
MODEL=$2
METHOD='feynmanSDdotS_mpi'
MODELPWD=`echo $MODEL|sed s/_phi/phi_/`
PWD=/home/mkompan/work/rg-graph/$MODELPWD/$METHOD/$1
NAME=`basename $PWD`
LIB=/home/mkompan/libs/pvegas
cd $PWD
PREFIX=/usr/lib64/openmpi/1.4-gcc
for i in `ls $NAME*func*.c`; do 
j=`echo $i|sed s/\.c$/\.o/`
echo $j
$PREFIX/bin/mpicc  -I$PREFIX/include -L$PREFIX/lib -L$LIB -I$LIB  ${i} -c -o ${j}
done


for i in `seq 0 5`; do
A=`ls $NAME*E$i.c 2>/dev/null|grep -v func`
if  [ "x$A" != "x" ]; then
B=`echo $A|sed s/\.c$/\.run/`
echo $B
$PREFIX/bin/mpicc -lm  -lpvegas_mpi -I . -L . -I$PREFIX/include -L$PREFIX/lib -L$LIB -I$LIB  ${A} `ls $NAME*func*E$i.o` -o ${B}
fi;
done 

