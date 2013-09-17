#!/usr/bin/python
# -*- coding: utf8

import phi4.common as common
import phi4.r as r
import phi4.ir_uv as ir_uv
import graphine
import rggraphutil


print common.defaultGraphHasNotIRDivergence(graphine.Graph.fromStr("ee12-ee3-444-555-5--"))
print r._generateSpinneys(graphine.Graph.fromStr("12-3-e444-555-e5--"))
print ir_uv.uvIndex(graphine.Graph.fromStr("14-222-3-4--"))
print ir_uv.uvIndex(graphine.Graph.fromStr("1113-2-3--"))
print common.defaultGraphHasNotIRDivergence(graphine.Graph.fromStr("ee12-ee3-444-444--"))
m = rggraphutil.zeroDict()
l = r._generateSpinneys(graphine.Graph.fromStr("e1112-e333-4-4--"))
for g in l:
    m[str(g)] += 1
print m


