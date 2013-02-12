#!/bin/sh

PWD=`pwd`
cd packages/Polynomial
./run_tests.sh || exit 1
cd $PWD

cd packages/Graphine
./run_tests.sh || exit 1
cd $PWD


