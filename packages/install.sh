#!/bin/bash

PWD1=`pwd`
echo $PWD1
for i in `ls -d base/GraphState base/Graphine RgGraphUtil RgGraphEnv Polynomial Reduction RStar MomentumRepresentation TaskScheduler UncertSeries`; do
   cd $PWD1
   cd $i
   echo install $i
   A=`python setup.py install --user`
   echo $A
   echo
done;
