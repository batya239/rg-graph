#!/bin/bash

export PYTHONPATH=`pwd`/momentumrepr

test_dir="momentumrepr/test"
for i in `ls $test_dir/*.py`; do 
    echo $i
    python $i
done
