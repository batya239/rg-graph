#!/bin/sh

MODEL=`cat model.txt`
NPOINTS=1000000
cd $PWD
for i in `cat _to_vmcluster.txt`; do 
TT=`qstat -a @pbs-vm.hpc.cc.spbu.ru|grep mkompan|wc -l`
M=`cat NQ-vm.txt`
while [ $TT -gt $M ]; do
#echo $TT
sleep 10
M=`cat NQ-vm.txt`
TT=`qstat -a @pbs-vm.hpc.cc.spbu.ru|grep mkompan|wc -l`
done
echo $i

sh rundiagM-vm.sh $i $NPOINTS
done
