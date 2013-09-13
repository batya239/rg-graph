#!/bin/bash

export PYTHONPATH=`pwd`/phi4

test_dir="phi4/test"
for i in `ls $test_dir/*.py`; do 
    echo $i
    python $i
done