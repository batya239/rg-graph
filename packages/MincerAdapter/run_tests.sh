#!/bin/bash

export PYTHONPATH=`pwd`/mincer

for i in `ls mincer/test/*.py`; do
    echo $i
    python $i 1>/dev/null || exit 1
done
