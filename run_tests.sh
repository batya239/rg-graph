#!/bin/sh

if [ ! -d "~/.rg-graph-storage" ]; then
  hg clone https://code.google.com/p/rg-graph-storage/ ~/.rg-graph-storage
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

cd packages/Polynomial
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/Graphine
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/MincerAdapter
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

cd packages/GFunctions
./run_tests.sh || exit 1
./setup.py install --user || exit 1
cd $PWD_

