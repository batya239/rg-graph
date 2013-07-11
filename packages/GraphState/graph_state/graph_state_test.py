#!/usr/bin/python
# -*- coding: utf8 -*-

import graph_state
import unittest


class TestFields(unittest.TestCase):
    def testCopy(self):
        fields = graph_state.Fields('ab')
        self.assertEqual(fields, fields.copy())
        swapped = fields.copy(swap=True)
        self.assertTrue(fields != swapped)
        self.assertEqual(fields, swapped.copy(swap=True))

    def testToFromString(self):
        fields = graph_state.Fields('ab')
        self.assertEqual(len(str(fields)), graph_state.Fields.STR_LEN)
        decoded = graph_state.Fields.fromStr(str(fields))
        self.assertEqual(fields, decoded)

    def testFieldsToFromString(self):
        string = 'aBcD'
        fields = graph_state.Fields.fieldsFromStr(string)
        self.assertEqual(len(fields), 2)
        self.assertEqual(graph_state.Fields.fieldsToStr(fields),
                         string)

    def testHash(self):
        first = graph_state.Fields('ab')
        second = graph_state.Fields('ba').copy(swap=True)
        self.assertTrue(first == second)
        self.assertTrue(hash(first) == hash(second))


class TestRainbow(unittest.TestCase):
    def testToFromStr(self):
        r = graph_state.Rainbow((0, 1))
        self.assertEqual(str(r), '(0, 1)')
        self.assertEqual(r, graph_state.Rainbow.fromStr(str(r)))


class TestEdge(unittest.TestCase):
    def testCompare(self):
        self.assertEqual(graph_state.Edge((0, 1)), graph_state.Edge((1, 0)),
            'Non-typed edges should not depend on nodes order.')
        self.assertTrue(graph_state.Edge((0, 1)) < graph_state.Edge((0, 2)))
        # (-1, 0) < (0, 1) < (1, -1) - Nickel ordering.
        self.assertTrue(graph_state.Edge((-1, 0)) < graph_state.Edge((0, 1)))
        self.assertTrue(graph_state.Edge((0, 1)) < graph_state.Edge((1, -1)))
        self.assertTrue(graph_state.Edge((-1, 0)) < graph_state.Edge((1, -1)))

    def testCompareWithFields(self):
        self.assertEqual(
                graph_state.Edge((0, 1), fields=graph_state.Fields('ab')),
                graph_state.Edge((1, 0), fields=graph_state.Fields('ba')))

        cmp_fields = cmp(graph_state.Fields('ab'), graph_state.Fields('ba'))
        cmp_edges = cmp(
                graph_state.Edge((0, 1), fields=graph_state.Fields('ab')),
                graph_state.Edge((0, 1), fields=graph_state.Fields('ba')))
        self.assertEqual(cmp_fields, cmp_edges)

    def testExternalNode(self):
        self.assertEqual(graph_state.Edge((0, 1), external_node=1),
                         graph_state.Edge((0, 2), external_node=2))

    def testAnnotateExternalField(self):
        edge = graph_state.Edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'))
        self.assertEqual(edge.fields.pair[0], 'a')
        self.assertEqual(edge.fields.pair[1], edge.fields.EXTERNAL)

    def testCopy(self):
        edge = graph_state.Edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'),
                colors=graph_state.Rainbow((0,)),
                edge_id=333)
        missed_attrs = [attr for attr in edge.__dict__ if not edge.__dict__[attr]]
        self.assertEqual(len(missed_attrs), 0,
                'Attributes %s should be set.' % missed_attrs)

        self.assertEqual(edge, edge.copy())
        self.assertTrue(edge < edge.copy(node_map={0: 2}))

    def testHash(self):
        a = graph_state.Edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'))
        b = graph_state.Edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'))
        self.assertTrue(a == b)
        self.assertTrue(hash(a) == hash(b))


class TestGraphState(unittest.TestCase):
    def testInit(self):
        edges = tuple([graph_state.Edge(e)
                for e in [(-1, 0), (0, 1), (1, -1)]])
        state = graph_state.GraphState(edges, node_maps=[{}])
        self.assertEqual(state.sortings, [edges])

        state = graph_state.GraphState(edges, node_maps=[{0: 1, 1: 0}])
        self.assertEqual(state.sortings, [edges])

        state = graph_state.GraphState(edges, node_maps=[{}, {}])
        self.assertEqual(state.sortings, [edges, edges])

        state = graph_state.GraphState(edges, node_maps=[{1: 2}])
        self.assertTrue(state.sortings != [edges])

    def testSymmetries(self):
        edges = [graph_state.Edge((-1, 0), fields=graph_state.Fields('aa')),
                 graph_state.Edge((0, 1), fields=graph_state.Fields('aa')),
                 graph_state.Edge((1, -1), fields=graph_state.Fields('aa'))]
        state = graph_state.GraphState(edges)
        self.assertEqual(len(state.sortings), 2, 'Symmetry 0 <--> 1.')

        edges[1] = graph_state.Edge((0, 1), fields=graph_state.Fields('ab'))
        state = graph_state.GraphState(edges)
        self.assertEqual(len(state.sortings), 1, 'No symmetry 0 <--> 1.')

    def testHash(self):
        a = graph_state.GraphState((graph_state.Edge((0, -1)),))
        b = graph_state.GraphState((graph_state.Edge((0, -1)),))
        self.assertTrue(a == b)
        self.assertTrue(hash(a) == hash(b))

    def testToFromStr(self):
        edges = (graph_state.Edge((-1, 0)),
                 graph_state.Edge((0, 1)),
                 graph_state.Edge((1, -1)))
        state = graph_state.GraphState(edges)
        self.assertEqual(str(state), 'e1-e-::')

        decoded = graph_state.GraphState.fromStr(str(state))
        self.assertEqual(decoded.sortings[0], edges)

    def testToFromStrWithFields(self):
        edges = (graph_state.Edge((-1, 0), fields=graph_state.Fields('aa')),
                 graph_state.Edge((0, 1), fields=graph_state.Fields('ab')),
                 graph_state.Edge((1, -1), fields=graph_state.Fields('aa')))
        state = graph_state.GraphState(edges)
        self.assertEqual(str(state), 'e1-e-:0aab-0a-:')

        decoded = graph_state.GraphState.fromStr(str(state))
        self.assertEqual(decoded.sortings[0], edges)

    def testToFromStrWithColors(self):
        edges = (graph_state.Edge((-1, 0),
                                  colors=graph_state.Rainbow((1, 7))),)
        state = graph_state.GraphState(edges)
        self.assertEqual(str(state), "e-::['(1, 7)']")

        decoded = graph_state.GraphState.fromStr(str(state))
        self.assertEqual(decoded.sortings[0], edges)


if __name__ == "__main__":
    unittest.main()

