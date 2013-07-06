#!/bin/bash

export PYTHONPATH=`pwd`/mincer_adapter

for i in `ls mincer_adapter/test/*.py`; do
    echo $i
    python $i 1>/dev/null || exit 1
done
