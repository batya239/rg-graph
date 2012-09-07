#!/usr/bin/python
# -*- coding: utf8

import utils
from dummy_model import _phi3,_phi4
import sys
from graphs import Graph
import subgraphs

phi4=_phi4('dummy')

for nickel in utils.LoadFromGRC(sys.argv[1], phi4):
    g=Graph(nickel)
    g.GenerateNickel()
    phi4.SetTypes(g)
    g.FindSubgraphs(phi4)
    gas=g.asSubgraph()
    to_remove=subgraphs.DetectSauseges([gas]+g._subgraphs)
    if gas in to_remove:
        print "%s %s S"%(nickel, g.sym_coef())
    else:
        print "%s %s"%(nickel, g.sym_coef())