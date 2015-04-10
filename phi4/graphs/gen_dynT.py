#!/usr/bin/python
# -*- coding: utf8
import os

from graph_state_builder_with_fields import gs_builder
import sys

import subgraphs
from methods.sd_tools import FeynmanSubgraphs
from dummy_model import _phi3_dyn, _phi4_dyn

import dynamics


model = _phi4_dyn("phi4_dyn_test")
methodName = "simpleSDT"

gs = gs_builder.graph_state_from_str("e12|23|4|e5|55||:0A_aA_aA|Aa_aA|aA|0a_Aa|aA_aA||")
print str(gs)

dG = dynamics.DynGraph(gs)
FeynmanSubgraphs(dG, model)
#dG.FindSubgraphs(model)
#subgraphs.RemoveTadpoles(dG)

staticCDET = dynamics.generateStaticCDET(dG, model)
print staticCDET[0]
print "lines:"
for line in dG._lines:
    print line
print "\nsubgraphs:"
for i in range(len(dG._subgraphs)):
    print "a%s "%i, dG._subgraphs

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
