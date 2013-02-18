#!/usr/bin/python
# -*- coding: utf8


import graph_state
import sys

import subgraphs
from dummy_model import _phi3_dyn, _phi4_dyn

import dynamics

import polynomial

model = _phi4_dyn("phi4_dyn_test")

gs = graph_state.GraphState.fromStr(sys.argv[1])
#gs = graph_state.GraphState.fromStr("e12-e3-45-45-5--:0AaAaA-0aaA-aAaa-aaaa-aA--:")
#gs = graph_state.GraphState.fromStr("e12-e3-33--:0AaAaA-0aaa-aAaa--:")
print str(gs)

dG = dynamics.DynGraph(gs)

dG.FindSubgraphs(model)
subgraphs.RemoveTadpoles(dG)

D, C = map(lambda x: dynamics.relabel(x, dynamics.rules), dynamics.genStatic_D_C(dG))
E = [(x,) for x in dG._qi2l]
T = dynamics.genStaticT(dG)
staticCDET = (C, D, E, T)

for tVersion in dynamics.TVersions(dG):
    print
    print "tVersion = ", tVersion
    print "subgraphs :"
    Components = dynamics.generateCDET(dG, tVersion, staticCDET=staticCDET)
    print "C = %s\nD = %s\nE = %s\nT = %s\n" % tuple(Components)
