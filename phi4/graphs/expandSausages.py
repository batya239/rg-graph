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
    to_remove = subgraphs.DetectSauseges_([gas] + g._subgraphs)
    if gas in to_remove:
        if len(to_remove[gas]) == 2:
            print 'result["%s"] = multiply(result["%s"], result["%s"])' % (nickel, to_remove[gas][0].Nickel(), to_remove[gas][1].Nickel())
        else:
            raise ValueError("more than 2 subgraphs: %s" % map(lambda x: str(x.Nickel()), to_remove[gas]))


