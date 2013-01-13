#!/usr/bin/python
# -*- coding: utf8
import sys

import bw_code_generator as bw

strategies = ("A", "B", "C", "X",)
strategies = ("A",)
name = sys.argv[1]

for strategy in strategies:
    bw.generate_code(name, strategyName="STRATEGY_%s" % strategy, startOrder=0, endOrder=0,
                     fileName="bw_code/%s_%s.cc" % (name, strategy))
