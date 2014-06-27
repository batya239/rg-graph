#!/usr/bin/python
import graph_state
import time
import sys
from graph_state_builder import gs_builder
import graphine
from ym import uv_condition, uv_index, nonzero_momenta_counterterm

connected = graphine.filters.connected
no_tadpoles = graphine.filters.no_tadpoles
one_irreducible = graphine.filters.one_irreducible


# gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|e7|e7||:0_0_0|0_0|0_0|1_0|0|0_0|0_1||")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|e7|e|:0_0_0|0_0|0_0|0|0_0|0|0_0|0|0|")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|78|9|e9|e|:0_0_0|0_0|0_0|0|0_0|0|0_0|0|0_0|0|")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|67|68|9|e9|e9||:0_0_0|0_0|0_0|0|0_0|1_0|0|0_0|0_1||")
# gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|78|79||e9|e|:0_0_0|0_0|0_0|1_0|0|0_0|1_0||0_0|0|")
# gs = gs_builder.graph_state_from_str("e12|e3|45|67|e8|68|9|e9|9||:0_0_0|0_0|0_0|12_0|0_0|0_0|0|0_12|0||")
# gs = gs_builder.graph_state_from_str("e12|e3|45|46|7|e8|79|8|9|e|:0_0_0|0_0|1_0|0_2|2|0_1|0_0|0|0|0|")
# gs = gs_builder.graph_state_from_str("e12|34|56|e7|67|e8|8|9|9|e|:0_0_0|0_1|2_0|0_1|0_0|0_0|2|0|0|0|")
# gs = gs_builder.graph_state_from_str("e12|e34|35|6|67|e67||e|:0_0_0|0_0_0|0_0|0|0_0|0_0_0||0|")
# gs = gs_builder.graph_state_from_str("e12|34|35|67|e6|e7|8|8|e|:0_0_0|0_0|0_0|0_0|0_0|0_0|0|0|0|")
gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|89|8A|B|eB|eB||:0_0_0|0_0|0_0|0|0_0|0|1_0|0_0|0|0_1|0_0||")

# gs = gs_builder.graph_state_from_str(sys.argv[1])
print gs


graph = graphine.Graph(gs)
start = time.time()
print "graph UV index: ", uv_index(graph)
print "subgraphs:"
for subgraph in graph.x_relevant_sub_graphs(one_irreducible + no_tadpoles + uv_condition + nonzero_momenta_counterterm):
    print subgraph

print time.time()-start

