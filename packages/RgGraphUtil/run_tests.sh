#!/bin/bash

export PYTHONPATH=`pwd`/rggraphutil

for i in `ls rggraphutil/test/*.py`; do
    echo $i
    python $i 1>/dev/null || exit 1
done
