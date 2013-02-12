#!/bin/sh

PWD_=`pwd`
cd packages/GraphState
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


