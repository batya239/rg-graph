#!/usr/bin/python
import os
import sys

__author__ = 'mkompan'

qsubScriptTemplate = """#!/bin/sh

PWD={diagramdir}
POINTS={points}
NODES={nodes}
NODESPPN="{nodesppn}"
ITER={iter}
DELTA={delta}
cd $PWD
for PROG in `ls *.run`; do
cat << EOF | qsub  -N $PROG -l nodes=$NODESPPN  -q long@pbs-vm.hpc.cc.spbu.ru -W group_list=vcluster

export PATH={mpidir}/bin:$PATH
export LD_LIBRARY_PATH={mpidir}/lib64:{libdir}:{mpidir}/../lib/
PREFIX={mpidir}

echo $PROG $POINTS $NODES $ITER

NODEFILE=\$PBS_NODEFILE

for adrr in `cat \$PBS_NODEFILE`;do
   ssh \$adrr /usr/local/sbin/cleanipcs;
done

cd {diagramdir}
echo "\$PREFIX/bin/mpirun  -machinefile \$NODEFILE  -x LD_LIBRARY_PATH  -np $NODES $PROG $POINTS $NODES $ITER"
\$PREFIX/bin/mpirun  -machinefile \$NODEFILE  -x LD_LIBRARY_PATH  -np $NODES $PROG $POINTS $NODES $ITER $DELTA |tee ${{PROG}}-curr.log

EOF
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

for arg in sys.argv[3:]:
    if arg.find("=") > 0:
        exec(arg)

diagramdir = os.path.join(append_home(workdir), graph_name)
libdir = append_home(libdir)
mpidir = append_home(mpidir)



print qsubScriptTemplate.format(diagramdir=diagramdir,
                                libdir=libdir,
                                mpidir=mpidir,
                                points=points,
                                iter=iterations,
                                nodes=nodes,
                                nodesppn=nodesppn,
                                delta=delta)