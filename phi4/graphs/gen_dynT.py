#!/usr/bin/python
# -*- coding: utf8
import os

import graph_state
import sys

import subgraphs
from dummy_model import _phi3_dyn, _phi4_dyn

import dynamics


model = _phi4_dyn("phi4_dyn_test")
methodName = "simpleSDT"

gs = graph_state.GraphState.fromStr(sys.argv[1])
print str(gs)

dG = dynamics.DynGraph(gs)

dG.FindSubgraphs(model)
subgraphs.RemoveTadpoles(dG)

dG = dynamics.DynGraph(gs)
dG.FindSubgraphs(model)
subgraphs.RemoveTadpoles(dG)

staticCDET = dynamics.generateStaticCDET(dG, model)


for tVersion in dynamics.TVersions(dG):
    print
    print "tVersion = ", tVersion
    name = dynamics.Replace("%s_%s" % (gs, tVersion))
    dirName = '%s/%s/%s/' % (model.workdir, methodName, name)
    try:
        os.mkdir('%s/%s' % (model.workdir, methodName))
    except:
        pass
    try:
        os.mkdir(dirName)
    except:
        pass

    fileName = dynamics.Replace("%s/dyn_sectors_templ.py" % dirName)
    print fileName
    tCuts = dynamics.TCuts(dG, tVersion)

    subGraphDims = map(lambda x: dynamics.EffectiveSubgraphDim(x, tCuts, model), dG._subgraphs)
    subGraphOps = ''
    for i in range(len(subGraphDims)):
        subGraphOps += 'to1(\'a%s\'),' % i if subGraphDims[i] < 0 else 'D%s(\'a%s\'),' % (subGraphDims[i] / 2 + 1, i)

    print subGraphOps

    f = open(fileName, 'w')
    f.write("""#!/usr/bin/python
# -*- coding:utf8
from dynamics import D1, D2, to1, mK0, mK1
graphName = \"%s\"

tVersion = %s

sectors = [
]
""" % (gs, tVersion))
