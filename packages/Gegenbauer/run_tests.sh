#!/bin/bash

export PYTHONPATH=`pwd`/gegenbauer

test_dir="gegenbauer/test"
for i in `ls $test_dir/*.py`; do 
    echo $i
    python $i 1>/dev/null || exit 1
done
