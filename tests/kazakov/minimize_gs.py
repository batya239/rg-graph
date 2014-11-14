#!/usr/bin/python
__author__ = 'mkompan'

import sys
from graph_state_builder_dual import gs_builder

gs = gs_builder.graph_state_from_str(sys.argv[1])
print sys.argv[1]
print gs