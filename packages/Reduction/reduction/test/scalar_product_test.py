#!/usr/bin/python
# -*- coding: utf8
__author__ = 'dima'

import unittest
import scalar_product
import graphine
import graph_state
import reductor
import two_and_three_loops


def _stupid_scalar_product_extractor(shrunk, initial_graph):
    for e1, e2 in zip(shrunk.allEdges(nickel_ordering=True), initial_graph.allEdges(nickel_ordering=True)):
        scalar_product_direction = e2.arrow.as_numeric()
        if scalar_product_direction:
            sp = scalar_product.ScalarProduct(e1.colors[1], (1, 0, 0), power=1, sign=scalar_product_direction)
            yield sp


class ScalarProductTest(unittest.TestCase):
    def test_tbubble(self):
        gs = graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.graph_state_from_str("e12|23|3|e|:(0,0)_(1,0)_(1,0)|(1,0)_(1,0)|(1,0)|(0,0)|:0_0_0|>_0|0|0|")
        g = graphine.Graph(gs)
        res = two_and_three_loops.TWO_LOOP_REDUCTOR.calculate(g, scalar_product_aware_function=_stupid_scalar_product_extractor)
        self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()