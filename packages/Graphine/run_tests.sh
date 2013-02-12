#!/bin/bash

export PYTHONPATH=`pwd`/graphine

test_dir="graphine/test"
for i in `ls $test_dir/*.py`; do 
    echo $i
    python $i 1>/dev/null || exit 1
done
