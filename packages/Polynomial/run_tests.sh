#!/bin/bash

export PYTHONPATH=`pwd`/polynomial

for i in `ls polynomial/test/*.py`; do 
    echo $i
    python $i 1>/dev/null || exit 1
done
