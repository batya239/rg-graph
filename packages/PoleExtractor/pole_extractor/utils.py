__author__ = 'gleb'

import graphine
import graph_state


def tau_differentiate(g):
    seen = set()
    unreduced = tuple()
    if isinstance(g, graphine.Graph):
        new_vertex = max(g.vertices()) + 1
        for edge in g.internalEdges():
            g1 = g.deleteEdge(edge)
            new_edges = map(lambda x: graph_state.Edge(x), ([new_vertex, edge.nodes[0]],
                                                            [new_vertex, edge.nodes[1]],
                                                            [new_vertex, g.externalVertex]))
            unreduced += tuple([g1.addEdges(new_edges)])
        return tuple((unreduced.count(x), x) for x in unreduced if str(x) not in seen and not seen.add(str(x)))

    elif isinstance(g, tuple):
        for x in g:
            unreduced += tuple(map(lambda y: (y[0] * x[0], y[1]), tau_differentiate(x[1])))

        result = tuple()
        for i, x in enumerate(unreduced):
            if str(x[1]) not in seen:
                seen.add(str(x[1]))
                new_num = 0
                for y in unreduced[i:]:
                    if str(y[1]) == str(x[1]):
                        new_num += y[0]
                result += tuple([(new_num, x[1]), ])
        return result

g = graphine.Graph.fromStr('112-3-33--')
print tau_differentiate(g)
print tau_differentiate(tau_differentiate(g))
print tau_differentiate(tau_differentiate(tau_differentiate(g)))
print
g = graphine.Graph.fromStr('123-23-3--')
print tau_differentiate(g)
print tau_differentiate(tau_differentiate(g))
print tau_differentiate(tau_differentiate(tau_differentiate(g)))
print