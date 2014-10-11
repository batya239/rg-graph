#!/bin/bash

export PYTHONPATH=`pwd`/rstar

for i in `ls rstar/test/*.py`; do
    echo $i
    python $i 1>/dev/null || exit 1
done
