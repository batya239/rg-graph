#!/bin/sh

cd $PWD
MODEL=`cat modelN.txt`
for i in `cat _to_tpclusterN.txt`; do 
TT=`qstat -a @pbs-tp.hpc.cc.spbu.ru|grep mkompan|wc -l`
M=`cat NQ-tp.txt`
while [ $TT -gt $M ]; do
#echo $TT
sleep 10
M=`cat NQ-tp.txt`
TT=`qstat -a @pbs-tp.hpc.cc.spbu.ru|grep mkompan|wc -l`
done
echo $i
sh qsub-gen-sectorsN-tp.sh $i $MODEL
done
