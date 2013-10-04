#!/usr/bin/python
# -*- coding: utf8

import phi4.common as common
import phi4.r as r
import phi4.ir_uv as ir_uv
import graphine
import rggraphutil

print common.defaultGraphHasNotIRDivergence(graphine.Graph.fromStr("e112-33-e3--"))
print common.defaultGraphHasNotIRDivergence(graphine.Graph.fromStr("e112-33-3-e-"))
print common.defaultGraphHasNotIRDivergence(graphine.Graph.fromStr("e112-33-3-e-"))


print [x for x in graphine.Graph.fromStr("e1123-23-e4-4--").xRelevantSubGraphs(filters=graphine.filters.oneIrreducible
                                                   + graphine.filters.isRelevant(ir_uv.UVRelevanceCondition())
                                                   + r._is_1uniting,
                                           cutEdgesToExternal=False)]


print [x for x in graphine.Graph.fromStr("e1234-e455-5-4---:0000iooi00-00000000-00-00---:").xRelevantSubGraphs(filters=common.defaultSubgraphUVFilter, cutEdgesToExternal=True)]
