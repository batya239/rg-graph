#!/bin/bash

export PATH=$HOME/bin:$PATH
export LD_LIBRARY_PATH=$HOME/libs/ginac64

./$1 &
sleep 10
kill -9 %1

