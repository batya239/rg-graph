import copy
import time
import itertools
import sys
import graph_state

__author__ = 'mkompan'

from graph_state_builder_dual import gs_builder as gs_builder_dual
from graph_state_builder_loops import gs_builder, Rainbow
import graphine
import dual_lib



# gs = gs_builder.graph_state_from_str("e12|e3|34|5|e5|e|:")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|e7|e|:")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|89|8A|B|eB|eB||:")
# gs = gs_builder.graph_state_from_str("e12|23|4|e5|67|89|7A|B|eC|eC|BD|D|D||:")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|78|9|9A|B|BC|D|eD|e|:")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|89|8A|B|eC|BD|C|D|e|:")

gs = gs_builder.graph_state_from_str("%s:" % sys.argv[1])
print gs

g = graphine.Graph(gs)



start = time.time()
try:
    coloured_graph = dual_lib.graph_with_momenta(g)
    dual = dual_lib.dual_graph(coloured_graph)
except:
    print "Failed to construct dual graph"
    sys.exit(1)
finally:
    print time.time()-start


pairs = dual_lib.generate_pairings(dual)
if len(pairs) == 0:
    print "no pairings"
    sys.exit(1)

print coloured_graph
print g, "dual:", dual
print "pairs", pairs
print time.time()-start

# for pairing in pairs:
#     for pair in pairing:
#         print pair, dual_lib.check_pair(pair, dual)
#     print
