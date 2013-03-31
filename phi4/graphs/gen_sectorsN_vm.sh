#!/bin/sh

cd $PWD
MODEL=`cat modelN.txt`
for i in `cat _to_vmclusterN.txt`; do 
TT=`qstat -a @pbs-vm.hpc.cc.spbu.ru|grep mkompan|wc -l`
M=`cat NQ-vm.txt`
while [ $TT -gt $M ]; do
#echo $TT
sleep 10
M=`cat NQ-vm.txt`
TT=`qstat -a @pbs-vm.hpc.cc.spbu.ru|grep mkompan|wc -l`
done
echo $i
sh qsub-gen-sectorsN-vm.sh $i $MODEL
done
