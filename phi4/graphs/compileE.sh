#!/bin/bash

#set -x
export LD_LIBRARY_PATH=~/soft/pvegas
NAME=$1
for j in  `ls $NAME*E*.c|grep -v func`; do 
#   echo $j
   NN=`echo $j|sed 's/.*_E\([0-9]*\)\.c/\1/g'`
#   echo 'n=' $NN
   for i in `ls $NAME*func*_E$NN*|grep  "\.c$"`; do 
      echo "Compiling $i ..."
      A=`echo $i|sed 's/\.c$/\.o/'`
      gcc $i -lm -O2 -c -o $A
   done
#   echo $NN
   CODE=`ls $NAME*E${NN}.c|grep -v func`

   gcc $CODE $NAME*func*_E$NN.o -lm -lpvegas -o ${NAME}_E$NN -I . -I ~/soft/pvegas -L ~/soft/pvegas

done
