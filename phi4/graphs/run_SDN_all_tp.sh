#!/bin/sh

MODEL=`cat modelN.txt`
NPOINTS=1000000
cd $PWD
for i in `cat _to_tpclusterN.txt`; do 
TT=`qstat -a @pbs-tp.hpc.cc.spbu.ru|grep mkompan|wc -l`
M=`cat ~/tmp/NQ-tp.txt`
while [ $TT -gt $M ]; do
#echo $TT
sleep 10
M=`cat ~/tmp/NQ-tp.txt`
TT=`qstat -a @pbs-tp.hpc.cc.spbu.ru|grep mkompan|wc -l`
done
echo $i

sh rundiagN-tp.sh $i $NPOINTS
done
