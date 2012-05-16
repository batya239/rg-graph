#!/bin/bash

#set -x
export LD_LIBRARY_PATH=~/soft/pvegas
NAME=$1

for i in `ls $NAME*func*|grep  "\.c$"`; do A=`echo $i|sed 's/\.c$/\.o/'`; if [ ! -f $A ] && [ ! -f ${A}.lock ]; then echo "Compiling $i ..."; touch ${A}.lock; A=`echo $i|sed 's/\.c$/\.o/'`; gcc $i -lm -O2 -c -o $A;fi; done

CODE=`ls $NAME*.c|grep -v func`

#gcc $CODE $NAME*func*.o -lm -lpvegas -o $NAME -I . -I ~/soft/pvegas -L ~/soft/pvegas
