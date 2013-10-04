#!/bin/sh


#storage for operations results
if [ ! -d "~/.rg-graph-storage" ]; then
  hg clone https://code.google.com/p/rg-graph-storage/ ~/.rg-graph-storage
else
  hg revert --all
  hg pull -u
fi


PWD_=`pwd`
cd packages/GraphState
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/RgGraphUtil
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/Graphine
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/RgGraphEnv
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/Polynomial
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/Phi4
./setup.py install --user || exit 1
./run_tests.sh || exit 1
cd $PWD_

