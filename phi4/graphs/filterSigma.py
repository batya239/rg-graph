#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'


from dummy_model import _phi4
import sys
from graphs import Graph
import subgraphs

phi4 = _phi4('dummy')
phi4.nodes_dim = {1: 0, 2: 2}

for item in open(sys.argv[1]).readlines():
    nickel = item.strip()
    g = Graph(nickel)
    g.GenerateNickel()
    phi4.SetTypes(g)
    g.FindSubgraphs(phi4)
    gas = g.asSubgraph()
    to_remove = subgraphs.DetectSauseges([gas] + g._subgraphs)
    if gas not in to_remove:
        g.RemoveSubgaphs(to_remove)
        subgraphs.RemoveTadpoles(g)
        for sub in g._subgraphs:
            if sub.CountExtLegs() == 2:
                print "%s" % (nickel)
                break