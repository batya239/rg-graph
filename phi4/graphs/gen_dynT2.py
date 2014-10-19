#!/usr/bin/python
# -*- coding: utf8
import os

from graph_state_builder_with_fields import gs_builder
import sys

import subgraphs
from dummy_model import _phi3_dyn, _phi4_dyn
from methods.sd_tools import FeynmanSubgraphs

import dynamics


model = _phi4_dyn("phi4_dyn_test")
methodName = "simpleSDT"

gs = gs_builder.graph_state_from_str(sys.argv[1])
print str(gs)

dG = dynamics.DynGraph(gs)
FeynmanSubgraphs(dG, model)
#dG.FindSubgraphs(model)
#subgraphs.RemoveTadpoles(dG)

print "\nsubgraphs:"
for i in range(len(dG._subgraphs)):
    print "a%s "%i, dG._subgraphs

staticCDET = dynamics.generateStaticCDET(dG, model)

model = _phi4_dyn("phi4_dyn_test")

for tVersion in dynamics.TVersions(dG):
    print
    print "tVersion = ", tVersion
    name = dynamics.Replace("%s_%s" % (gs, tVersion))
    dirName = '%s/%s/%s/' % (model.workdir, methodName, name)
    inputFileName = '%s/dyn_sectors_templ.py' % dirName
    exec(open(inputFileName).read())
    print "sectors = ", sectors

    gs = gs_builder.graph_state_from_str(graphName)

    dG = dynamics.DynGraph(gs)
    print dG._lines
    FeynmanSubgraphs(dG, model)
    Components = dynamics.generateCDET(dG, tVersion, model=model)

    C, D, E, T = Components
    #d=4-2*e

    expr = C * D * E * T
    print "C = %s\nD = %s\nE = %s\nT = %s\n" % (C, D, E, T)

    variables = expr.getVarsIndexes()
    print "variables: ", variables

    sdtTree = dynamics.Tree(None)

    for sector, ops in sectors:
        print sector, ops
        sdtTree.addSector(sector)



    fileName = dynamics.Replace("%s/dyn_sectors.py" % dirName)
    print fileName
    tCuts = dynamics.TCuts(dG, tVersion)

    subGraphDims = map(lambda x: dynamics.EffectiveSubgraphDim(x, tCuts, model), dG._subgraphs)
    subGraphOps = ''
    for i in range(len(subGraphDims)):
        subGraphOps += '\"to1(\'a%s\')\",' % i if subGraphDims[i] < 0 else '\"D%s(\'a%s\')\",' % (subGraphDims[i] / 2 + 1, i)

    print subGraphOps

    variables = dG._qi.keys()
    conservations = dG._cons

    nLoops = dG.NLoops()
    # print variables
    # print conservations
    # print r4Loops

    # for sector in dynamics.xTreeElement2(sdtTree):
    #     print  "    (%s, (  ))," % (sector)

#    sectorTree = dynamics.generateStaticSpeerTree(variables, conservations, r4Loops, tree=sdtTree)
    sectorTree = dynamics.generateDynamicSpeerTree(dG, tVersion, model, tree=sdtTree)
    sectorString = ""
#    for sector in dynamics.xTreeElement2(sectorTree):
    for sector in dynamics.xTreeElement2(sectorTree):
        sectorString += "    (%s, (%s)),\n" % (sector, subGraphOps)

    # print sectorString
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
