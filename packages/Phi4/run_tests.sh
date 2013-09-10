#!/bin/bash

export PYTHONPATH=`pwd`/gfunctions

test_dir="gfunctions/test"
for i in `ls $test_dir/*.py`; do 
    echo $i
    python $i 1>/dev/null || exit 1
done

test_dir="mincer_adapter/test"
for i in `ls $test_dir/*.py`; do
    echo $i
    python $i 1>/dev/null || exit 1
done
