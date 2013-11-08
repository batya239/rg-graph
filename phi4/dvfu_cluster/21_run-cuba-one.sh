#!/bin/bash

## Исполняем все cuba-файлы, которые лежат в конкретной папке <diag>,
## вычисления начинаем на узле <start-node> и далее увеличивем на 1
if [[ $# != 2 ]]; then
    echo "usage: ./21_run-cuba-one <diag> <start-node>"
    echo "example: ./21_run-cuba-one e112-34-e34-55-55--/ 17"
    exit
else
    diag=$1
    START=$2
fi
CUR_DIR=`pwd`
WORKDIR=$HOME'/work/rg-graph/phi_4_d2_s2/feynmanSDdotSF_mpi/'
METHOD='cuhre'
cd $WORKDIR$1
        for c in `ls cuba__??.run`
            do
                NUM=`echo $c | cut -c 7,8`
                echo "ssh to n"$START"... start cuba__"$NUM".run"
                #OUT="out_"$NUM"_"${PWD##*/}"_"$METHOD"_1M_e-6_e-12"
                OUT="out_"$NUM"_"${PWD##*/}"_"$METHOD"_50M_e-8_e-12"
                echo "result will be stored in "$OUT
                #ssh n$START nohup $WORKDIR$diag$c 3 1000000 1e-6 1e-12 > $OUT &
                ssh n$START nohup $WORKDIR$diag$c 3 50000000 1e-8 1e-12 > $OUT &
                START=$((START+1))
            done
cd ..
cd $CUR_DIR
#python get_answer.py $METHOD
#python compare.py $METHOD
