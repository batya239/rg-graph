#!/usr/bin/python
# -*- coding: utf8


import sys


import graph_state

from dummy_model import _phi3_dyn

model = _phi3_dyn("phi3_dyn_test")


gs = graph_state.GraphState.fromStr(sys.argv[1])
print str(gs)

