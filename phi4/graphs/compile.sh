#!/bin/bash

#set -x
export LD_LIBRARY_PATH=~/soft/pvegas
NAME=$1

for i in `ls $i*func*|grep  "\.c$"`; do echo "Compiling $i ..."; A=`echo $i|sed 's/\.c$/\.o/'`; gcc $i -lm -c -o $A; done

CODE=`ls $NAME*.c|grep -v func`

gcc $CODE $NAME*func*.o -lm -lpvegas -o $NAME -I . -I ~/soft/pvegas -L ~/soft/pvegas
