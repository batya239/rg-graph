#!/bin/sh
export PYTHONPATH=`pwd`
python nickel/nickel_test.py || exit 1
python graph_state/graph_state_test.py || exit 1 
