#/bin/bash

#PBS -V
#PBS -S /bin/bash
#PBS -q infi@pbs-vm.hpc.cc.spbu.ru 
#PBS -W group_list=vcluster
#PBS -l nodes=1:ppn=4
#PBS -j oe
#PBS -N diag_calc

if [ -z $diag ]
then
    echo "diag name is unset"
    exit
fi

cd $HOME/rg-graph/phi4/graphs/phi4_dyn/simpleSDT/$diag

../run_cuba.sh $Enum
