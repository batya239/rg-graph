#!/usr/bin/python
# -*- coding: utf8

import collections
try:
    import swiginac
    numeric = swiginac.numeric
    factorial = swiginac.factorial
except ImportError:
    try:
        import sympy
        numeric = sympy.numer
        factorial = sympy.factorial
    except ImportError:
        print "One of swiginac or sympy is required"
        exit(1)


def symmetry_coefficient(gs):
    """
    Calculates symmetries factor of given diagram
    :param gs: must be instance of `graphine.Graph`
    """
    gs = gs.to_graph_state()
    external_edge_fields = collections.defaultdict(lambda: 0)
    edges_count = collections.defaultdict(lambda: 0)
    bubbles = dict()
    for edge in gs.edges:
        n1, n2 = edge.nodes
        if n1 == n2:
            bubbles[edge] += 1
        edges_count[edge] += 1

        if edge.is_external():
            if edge.fields is None:
                field = None
            else:
                field = frozenset(edge.fields.pair)
            external_edge_fields[field] += 1

    c = numeric(1)

    for n in external_edge_fields.values():
        c *= factorial(numeric(n))

    for n in edges_count.values():
        c /= factorial(numeric(n))
    trace = reduce(lambda x, y: x + y, [0] + bubbles.values())
    c /= numeric(2) ** trace

    return c / numeric(len(gs.sortings))