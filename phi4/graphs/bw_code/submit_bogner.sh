#!/bin/bash

name=$1

cat bogner.tmpl|sed "s/<PROG>/$name/"|qsub -N $name -l nodes=1 -q long@pbs-vm.hpc.cc.spbu.ru -W group_list=vcluster
