#!/usr/bin/python
# -*- coding: utf8
import os

import sys
import re

from graph_state_builder_with_fields import gs_builder
import polynomial.sd_lib as sd_lib
import polynomial

import subgraphs
from dummy_model import _phi3_dyn, _phi4_dyn

import dynamics


model = _phi4_dyn("phi4_dyn_test")
methodName = "simpleSDT"
dynamics.method_name = methodName

points = int(sys.argv[2])
graphName = sys.argv[1]
gs = gs_builder.graph_state_from_str(graphName)
print str(gs)
dG = dynamics.DynGraph(gs)

if len(sys.argv) == 4:
    tVersions = [eval(sys.argv[3])]
else:
    tVersions = dynamics.TVersions(dG)
pwd = os.environ['PWD']

for tVersion_ in tVersions:
    print
    print "tVersion = ", tVersion_
    os.chdir(pwd)
    name = dynamics.Replace("%s_%s" % (gs, tVersion_))
    dirName = '%s/%s/%s/' % (model.workdir, methodName, name)
    print dirName
    fileName = "%s/dyn_sectors.py" % dirName
    exec (open(fileName).read())

    gs = gs_builder.graph_state_from_str(graphName)
    tVersion = tVersion

    dG = dynamics.DynGraph(gs)

    neps = model.target - dG.NLoops() + 1

    (res, err) = dynamics.execute(name, model,
                                  neps=neps,
                                  points=points,
                                  threads=8)
    #calc_delta=0.0000000001))

    for i in range(len(res)):
        print i, (res[i], err[i])


