#!/bin/bash

export PYTHONPATH=`pwd`/rggraphenv

for i in `ls rggraphenv/test/*.py`; do
    echo $i
    python $i 1>/dev/null || exit 1
done
