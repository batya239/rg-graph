#!/bin/bash
for i in `ls | grep c`; do sed -i 's/#include <mpi.h>//g' $i; done
for i in `ls | grep c`; do sed -i 's/.*MPI.*//g' $i; done


#    sed  |sed 's/.*func_t_[1-9].*//g'
