__author__ = 'gleb'

import graphine
from graphine import filters

g = graphine.Graph.fromStr('e12-23-4-e5-55--')
ext_count = (2, 3)

sg_UV_filters = (filters.connected
                 + filters.oneIrreducible
                 + filters.noTadpoles)

subgraphsUV = filter(lambda x: x.externalEdgesCount() in ext_count,
                     [subg for subg in g.xRelevantSubGraphs(filters=sg_UV_filters,
                                                            resultRepresentator=graphine.Representator.asGraph,
                                                            cutEdgesToExternal=True)])

print str(g) + '\n' + str(subgraphsUV)