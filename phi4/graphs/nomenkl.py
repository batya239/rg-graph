#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4
from graphs import Graph

import graph_state


phi4=_phi4('dummy')

g1=Graph(sys.argv[1])


#phi4.reduce=False
name=str(g1.GenerateNickel())
print name, g1.sym_coef()

state = graph_state.GraphState([graph_state.Edge(e) for e in g1._edges()])
print state