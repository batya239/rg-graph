#!/usr/bin/python
import os
import sys

__author__ = 'mkompan'

compileScriptTemplate = """#!/bin/sh

PWD={diagramdir}
NAME=`basename $PWD`
LIB={libdir}
cd $PWD
PREFIX={mpidir}
for i in `ls $NAME*func*.c`; do
j=`echo $i|sed s/\.c$/\.o/`
echo $j
$PREFIX/bin/mpicc  -I$PREFIX/include -L$PREFIX/lib -L$LIB -I$LIB  ${{i}} -c -o ${{j}}
done


for i in `seq 0 10`; do
A=`ls $NAME*E$i.c 2>/dev/null|grep -v func`
if  [ "x$A" != "x" ]; then
B=`echo $A|sed s/\.c$/\.run/`
echo $B
$PREFIX/bin/mpicc -lm  -lpvegas_mpi -I . -L . -I$PREFIX/include -L$PREFIX/lib -L$LIB -I$LIB  ${{A}} `ls $NAME*func*E$i.o` -o ${{B}}
fi;
done
"""

def append_home(path):
    home = os.environ["HOME"]
    if path[0] != "/":
        return os.path.join(home, path)
    else:
        return path


#settings
exec(open(sys.argv[1]))
graph_name = sys.argv[2]



diagramdir = os.path.join(append_home(workdir), graph_name)
libdir = append_home(libdir)
mpidir = append_home(mpidir)



print compileScriptTemplate.format(diagramdir=diagramdir, libdir=libdir, mpidir=mpidir)