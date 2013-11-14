#!/bin/bash

export PYTHONPATH=`pwd`/reduction

test_dir="reduction/test"
for i in `ls $test_dir/*.py`; do 
    echo $i
    python $i
done