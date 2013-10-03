__author__ = 'gleb'

import graph_state
import nickel
from pole_extractor import feynman_construction
import rggraphutil.variable_aware_number as v_a_n

#unnickeled_node_pairs = [[-1, 0], [0, 1], [0, 2], [0, 3], [-1, 1], [1, 2], [1, 3], [-1, 2], [2, 3], [-1, 3]]
#node_pairs = nickel.Nickel(nickel=nickel.Canonicalize(unnickeled_node_pairs).nickel).edges
n_repr = nickel.Nickel(string='e123-e23-e3-e-')
f = feynman_construction.Feynman(n_repr, theory=4)
print f
print f._integrand * v_a_n.VariableAwareNumber(10, 1)
node_pairs = n_repr.edges
print n_repr.adjacent
for p in node_pairs:
    p.append(0)
node_pairs[0][2] = 3
node_pairs[3][2] = 1
gs = graph_state.GraphState(map(lambda x: graph_state.Edge(x[0:2], colors=x[2]), node_pairs))

