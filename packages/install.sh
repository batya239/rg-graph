#!/bin/bash

PWD1=`pwd`
echo $PWD1
for i in `ls -d GraphState Graphine GFunctions RgGraphUtil RgGraphEnv Polynomial MincerAdapter`; do
   cd $PWD1
   cd $i
   echo intstalling $i
   A=`python setup.py install --user`
   echo $A
   echo
done;
