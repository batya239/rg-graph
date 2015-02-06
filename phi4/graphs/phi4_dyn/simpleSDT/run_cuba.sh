#!/bin/bash


METHOD='cuhre'
MAX_POINTS='100000'
EPS_REL='1e-6'
EPS_ABS='1e-10'

if [ -z $1 ]
then
    echo "either E number or diag name is unset"
    exit
fi

if [ $METHOD = 'vegas' ]
    then MET_NUM=0
elif [ $METHOD = 'suave' ]
    then MET_NUM=1
elif [ $METHOD = 'divonne' ]
    then MET_NUM=2
elif [ $METHOD = 'cuhre' ]
    then MET_NUM=3
else
    echo "METHOD is not defined"
    exit
fi

for c in `ls *E$1.run`
    do
        ./$c $MET_NUM $MAX_POINTS $EPS_REL $EPS_ABS > out_${PWD##*/}_E$1_$MAX_POINTS_$METHOD.log
    done
