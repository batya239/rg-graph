#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import unittest
import scalar_product
import graphine
import reductor


def _stupid_scalar_product_extractor(shrunk, initial_graph):
    def _edge_has_scalar_product(edge):
        f = frozenset(edge.fields.pair)
        if f == frozenset(("i", "o")):
            return 1 if edge.fields.pair[0] == "i" else -1
        return 0

    for e1, e2 in zip(shrunk.allEdges(nickel_ordering=True), initial_graph.allEdges(nickel_ordering=True)):
        scalar_product_direction = _edge_has_scalar_product(e2)
        if scalar_product_direction:
            sp = scalar_product.ScalarProduct(e1.colors[1], (1, 0, 0), power=1, sign=scalar_product_direction)
            yield sp


class ScalarProductTest(unittest.TestCase):
    def test_tbubble(self):
        g = graphine.Graph.fromStr('e12-23-3-e-:000000-io00-00-00-:', initEdgesColor=True)
        res = reductor.TWO_LOOP_REDUCTOR.calculate(g,
                                                   scalar_product_aware_function=_stupid_scalar_product_extractor)
        self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()