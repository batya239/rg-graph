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

dG = dynamics.DynGraph(gs)
dG.FindSubgraphs(model)
subgraphs.RemoveTadpoles(dG)

staticCDET = dynamics.generateStaticCDET(dG)


def Replace(fileName):
    symbolsToReplace = '-:(),'
    res = fileName
    for symbol in symbolsToReplace:
        res = res.replace(symbol, "_")
    res = res.replace(' ', "")
    return res

#print dir(dG)
#print dG.Lines()

for tVersion in dynamics.TVersions(dG):
    print
    print "tVersion = ", tVersion
    fileName = Replace("%s_%s.py" % (gs, tVersion))
    print fileName
    tCuts = dynamics.TCuts(dG, tVersion)
    subgraphDims = map(lambda x: dynamics.EffectiveSubgraphDim(x, tCuts, model), dG._subgraphs)
    subgraphOps = ''
    for i in range(len(subgraphDims)):
        subgraphOps += 'to1(\'a%s\'),' % i if subgraphDims[i] < 0 else 'D%s(\'a%s\'),' % (subgraphDims[i] / 2 + 1, i)

    print subgraphOps

    sectorTree = dynamics.generateDynamicSpeerTree(dG, tVersion, model)
    sectorString = ""
    for sector in dynamics.xTreeElement2(sectorTree):
        sectorString += "    (%s, (%s)),\n" % (sector, subgraphOps)
    f = open(fileName, 'w')
    f.write("""#!/usr/bin/python
# -*- coding:utf8
from dynamics import D1, D2, to1, mK0, mK1
graphName = \"%s\"

tVersion = %s

sectors = [
%s
]
""" % (gs, tVersion, sectorString))
