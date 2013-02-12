#!/bin/sh

PWD=`pwd`
cd packages/Polynomial
./run_tests.sh || exit 1

