#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import unittest
import graphine
import forest


#noinspection PyProtectedMember
class ForestGenerationTestCase(unittest.TestCase):
    def test1(self):
        graph = graphine.Graph.fromStr("e1123|e34|445||5||")
        bubble = graph.edges(0, 1) + graph.edges(0, -1) + graph.edges(-1, 1)
        raw_forests = forest._generate_forests(graphine.Graph(bubble, renumbering=False), graph)
        forests = list()
        for raw_forest in raw_forests:
            forests.append(map(lambda f: f, raw_forest))
        self.assertEqual(len(forests), 8)
        for _forest in forests:
            print _forest

    def test2(self):
        graph = graphine.Graph.fromStr("e1123|e34|445||5||")
        eye = graph.edges(0, 1) + graph.edges(0, -1) + graph.edges(-1, 1) + graph.edges(2)
        raw_forests = forest._generate_forests(graphine.Graph(eye, renumbering=False), graph)
        forests = list()
        for raw_forest in raw_forests:
            forests.append(map(lambda f: f, raw_forest))
        self.assertEqual(len(forests), 2)
        for _forest in forests:
            print _forest

    def test3(self):
        graph = graphine.Graph.fromStr("e1123|e34|445||5||")
        gamma = graph.edges(0, 1) + graph.edges(0, -1) + graph.edges(-1, 1) + graph.edges(0, 3) + graph.edges(1, 4) + graph.edges(3, 4)
        gamma_as_graph = graphine.Graph(gamma, renumbering=False)
        print gamma_as_graph
        raw_forests = forest._generate_forests(gamma_as_graph, graph)
        forests = list()
        for raw_forest in raw_forests:
            forests.append(map(lambda f: f, raw_forest))
        for _forest in forests:
            print _forest
        self.assertEqual(len(forests), 3)


    def test4(self):
        graph = graphine.Graph.fromStr("e1123|e34|445||5||")
        gamma = graph.edges(0, 1) + graph.edges(0, -1) + \
                graph.edges(-1, 1) + graph.edges(0, 3) + \
                graph.edges(1, 4) + [graph.edges(3, 4)[0]] + \
                graph.edges(3, 5) + graph.edges(4, 5)
        gamma_as_graph = graphine.Graph(gamma, renumbering=False)
        raw_forests = forest._generate_forests(gamma_as_graph, graph)
        forests = list()
        for raw_forest in raw_forests:
            forests.append(map(lambda f: graphine.Graph(f), raw_forest))
        self.assertEqual(len(forests), 1)

    def test5(self):
        graph = graphine.Graph.fromStr("e1123|e34|445||5||")
        gamma = graph.edges(0, 1) + graph.edges(0, -1) + graph.edges(2) + \
                graph.edges(-1, 1) + graph.edges(0, 3) + \
                graph.edges(1, 4) + graph.edges(3, 4)
        gamma_as_graph = graphine.Graph(gamma, renumbering=False)
        raw_forests = forest._generate_forests(gamma_as_graph, graph)
        forests = list()
        for raw_forest in raw_forests:
            forests.append(map(lambda f: graphine.Graph(f), raw_forest))
        self.assertEqual(len(forests), 1)

if __name__ == '__main__':
    unittest.main()
