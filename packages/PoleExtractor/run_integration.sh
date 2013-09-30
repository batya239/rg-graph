#!/bin/sh
export OMP_NUM_THREADS=4
export CUBAVERBOSE=0
gcc -Wall -fopenmp -o integrate integrate.c -lm -lcuba -fopenmp
./integrate 
rm -rf integrate