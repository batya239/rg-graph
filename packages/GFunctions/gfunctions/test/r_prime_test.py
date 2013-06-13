#!/usr/bin/python
# -*- coding: utf8
import unittest
import graph_state
import graphine
import r_prime
import test

__author__ = 'daddy-bear'


class SubGraphReducerTestCase(test.GraphStorageAwareTestCase):
    def test1LoopDiagramPRime(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-e-::")))
        self.assertEquals("1/e", str(r_prime.doRPrime(g, r_prime.MSKOperation())))

    def testEyeRPrime(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e12-e22--::")))
        #self.assertEquals("1/e", str(r_prime.doRPrime(g, r_prime.MSKOperation())))


if __name__ == "__main__":
    unittest.main()