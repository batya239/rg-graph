#!/bin/sh
export OMP_NUM_THREADS=4
export CUBAVERBOSE=0
BASEDIR=$(dirname $0)
gcc -Wall -fopenmp -I${PWD} -o integrate ${BASEDIR}/integrate.c -lm -lcuba -fopenmp
./integrate
rm -rf integrate