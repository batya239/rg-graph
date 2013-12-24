#!/usr/bin/python
# -*- coding: utf8 -*-

import graph_state
import graph_state_property
import unittest

new_edge = graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge
new_properties = graph_state.DEFAULT_PROPERTIES_CONFIG.new_properties

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
        self.assertEqual(r, graph_state.Rainbow.fromObject(str(r)))

    def testFromStr2(self):
        r = graph_state.Rainbow.fromObject("\"asd\"")
        self.assertEqual(r.colors, ("asd",))

class TestEdge(unittest.TestCase):
    def testCompare(self):
        self.assertEqual(new_edge((0, 1)), new_edge((1, 0)),
            'Non-typed edges should not depend on nodes order.')
        self.assertTrue(new_edge((0, 1)) < new_edge((0, 2)))
        # (-1, 0) < (0, 1) < (1, -1) - Nickel ordering.
        self.assertTrue(new_edge((-1, 0)) < new_edge((0, 1)))
        self.assertTrue(new_edge((0, 1)) < new_edge((1, -1)))
        self.assertTrue(new_edge((-1, 0)) < new_edge((1, -1)))

    def testCompareWithFields(self):
        self.assertEqual(
                new_edge((0, 1), fields=graph_state.Fields('ab')),
                new_edge((1, 0), fields=graph_state.Fields('ba')))

        cmp_fields = cmp(graph_state.Fields('ab'), graph_state.Fields('ba'))
        cmp_edges = cmp(
                new_edge((0, 1), fields=graph_state.Fields('ab')),
                new_edge((0, 1), fields=graph_state.Fields('ba')))
        self.assertEqual(cmp_fields, cmp_edges)

    def testExternalNode(self):
        self.assertEqual(new_edge((0, 1), external_node=1),
                         new_edge((0, 2), external_node=2))

    def _testAnnotateExternalField(self):
        """
        suspicious
        """
        edge = new_edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'))
        self.assertEqual(edge.fields.pair[0], 'a')
        self.assertEqual(edge.fields.pair[1], edge.fields.EXTERNAL)

    def testCopy(self):
        edge = new_edge((0, 1),
                                external_node=1,
                                fields=graph_state.Fields('ab'),
                                colors=graph_state.Rainbow((0,)),
                                edge_id=333)
        missed_attrs = [attr for attr in edge.__dict__ if not edge.__dict__[attr]]
        self.assertEqual(len(missed_attrs), 0,
                'Attributes %s should be set.' % missed_attrs)

        self.assertEqual(edge, edge.copy())
        self.assertTrue(edge < edge.copy(node_map={0: 2}))

    def testHash(self):
        a = new_edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'))
        b = new_edge((0, 1), external_node=1,
                fields=graph_state.Fields('ab'))
        self.assertTrue(a == b)
        self.assertTrue(hash(a) == hash(b))

class TestGraphState(unittest.TestCase):
    def testGraphStateObjectsEqual(self):
        edges = tuple([new_edge(e, colors=graph_state.Rainbow((1, 2, 3)))for e in [(-1, 0), (0, 1), (1, -1)]])
        state1 = graph_state.GraphState(edges)
        state2 = graph_state.GraphState.fromStr(str(state1))
        self.assertEqual(state1, state2)

    def testEdgeId(self):
        edges = [new_edge(e, colors=(1, 2, 3)) for e in [(-1, 0), (0, 1), (1, -1)]]
        ids = map(lambda e: e.edge_id, edges)
        self.assertEqual(len(set(ids)), 3)

    def testInitWithDefaultValues(self):
        edges = tuple([new_edge(e) for e in [(-1, 0), (0, 1), (1, -1)]])
        state = graph_state.GraphState(edges, default_properties=new_properties(colors=graph_state.Rainbow((1, 1)),
                                                                                fields=graph_state.Fields.fromStr("qw")))
        for e in state.sortings[0]:
            self.assertEqual(e.colors, graph_state.Rainbow((1, 1)))
            if -1 in e.nodes:
                self.assertEqual(e.fields, graph_state.Fields.fromStr("0w"))
            else:
                self.assertEqual(e.fields, graph_state.Fields.fromStr("qw"))

        edges = list([new_edge(e) for e in [(-1, 0), (-1, 1)]])
        edges.append(new_edge((0, 1), colors=graph_state.Rainbow((2, 2)), fields=graph_state.Fields.fromStr("as")))
        state = graph_state.GraphState(edges,
                                       default_properties=new_properties(colors=graph_state.Rainbow((1, 1)),
                                                                         fields=graph_state.Fields.fromStr("0w")))
        for e in state.sortings[0]:
            if len(e.internal_nodes) == 1:
                self.assertEqual(e.colors, graph_state.Rainbow((1, 1)))
                self.assertEqual(e.fields, graph_state.Fields.fromStr("0w"))
            else:
                self.assertEqual(e.colors, graph_state.Rainbow((2, 2)))
                self.assertEqual(e.fields, graph_state.Fields.fromStr("as"))

    def testInit(self):
        edges = tuple([new_edge(e, colors=(1, 2, 3))
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
        edges = [new_edge((-1, 0), fields=graph_state.Fields('aa')),
                 new_edge((0, 1), fields=graph_state.Fields('aa')),
                 new_edge((1, -1), fields=graph_state.Fields('aa'))]
        state = graph_state.GraphState(edges)
        self.assertEqual(len(state.sortings), 2, 'Symmetry 0 <--> 1.')

        edges[1] = new_edge((0, 1), fields=graph_state.Fields('ab'))
        state = graph_state.GraphState(edges)
        self.assertEqual(len(state.sortings), 1, 'No symmetry 0 <--> 1.')

    def testHash(self):
        a = graph_state.GraphState((new_edge((0, -1)),))
        b = graph_state.GraphState((new_edge((0, -1)),))
        self.assertTrue(a == b)
        self.assertTrue(hash(a) == hash(b))

    def testToFromStr(self):
        edges = (new_edge((-1, 0)),
                 new_edge((0, 1)),
                 new_edge((1, -1)))
        state = graph_state.GraphState(edges)
        self.assertEqual(str(state), 'e1-e-')

        decoded = graph_state.GraphState.fromStr(str(state))
        self.assertEqual(decoded.sortings[0], edges)

    def testToFromStr1(self):
        actual_state = graph_state.GraphState.fromStr("e1-e-")
        self.assertEqual("e1-e-", str(actual_state))
        edges = (new_edge((-1, 0)),
                 new_edge((0, 1)),
                 new_edge((1, -1)))
        expected_state = graph_state.GraphState(edges)
        self.assertEqual(actual_state, expected_state)

    def testToFromStrWithFields(self):
        edges = (new_edge((-1, 0), fields=graph_state.Fields('0a')),
                 new_edge((0, 1), fields=graph_state.Fields('ab')),
                 new_edge((1, -1), fields=graph_state.Fields('a0')))
        state = graph_state.GraphState(edges)
        self.assertEqual(str(state), 'e1-e-::0a#ab-0a-')

        decoded = graph_state.GraphState.fromStr(str(state))
        self.assertEqual(decoded.sortings[0], edges)

    def testToFromStrWithColors(self):
        edges = (new_edge((-1, 0),
                                  colors=graph_state.Rainbow((1, 7))),)
        state = graph_state.GraphState(edges)
        self.assertEqual(str(state), "e-:(1, 7)-:")

        decoded = graph_state.GraphState.fromStr(str(state))
        self.assertEqual(decoded.sortings[0], edges)


class TestProperties(unittest.TestCase):
    def testCustomUndirectedProperty(self):
        class MyProperty(object):
            def __init__(self, a, b):
                self.a = a + 1
                self.b = b - 1

            def __str__(self):
                return str((self.a - 1, self.b + 1))

            def __eq__(self, other):
                return self.a == other.a and self.b == other.b

            def __hash__(self):
                return self.a + self.b * 31

            __repr__ = __str__

        class MyPropertyExternalizer(graph_state_property.PropertyExternalizer):
            def serialize(self, obj):
                return str(obj)

            def deserialize(self, string):
                return MyProperty(*eval(string))

        property_key = graph_state_property.PropertyKey(name='some_name',
                                                        is_directed=False,
                                                        externalizer=MyPropertyExternalizer())
        config = graph_state_property.PropertiesConfig.create(property_key)

        state = graph_state.GraphState.fromStr("e1-e-:(0,0)#(1,0)-(3,9)-", properties_config=config)
        es = set(map(lambda b: b.some_name, filter(lambda a: a.is_external(), state.edges)))
        self.assertEqual(es, set((MyProperty(3, 9), MyProperty(0, 0))))

    def testDirectedCustomProperty(self):
        class MyProperty(object):
            def __init__(self, a, b):
                self.a = a + 1
                self.b = b - 1

            def __str__(self):
                return str((self.a + 1, self.b - 1))

            __repr__ = __str__

            def __neg__(self):
                return MyProperty(self.b, self.a)

            def __eq__(self, other):
                return self.a == other.a and self.b == other.b

        class MyPropertyExternalizer(graph_state_property.PropertyExternalizer):
            def serialize(self, obj):
                return str(obj)

            def deserialize(self, string):
                return MyProperty(*eval(string))

        property_key = graph_state_property.PropertyKey(name='some_name',
                                                        is_directed=True,
                                                        externalizer=MyPropertyExternalizer())
        config = graph_state_property.PropertiesConfig.create(property_key)

        state = graph_state.GraphState.fromStr("e12-2-e-:(1,0)#(1,0)#(1,0)-(1,0)-(1,0)-", properties_config=config)
        e = state.edges[3]
        self.assertEqual(e.nodes, (-1, 1))
        self.assertEqual(e.some_name, MyProperty(1, 0))

if __name__ == "__main__":
    unittest.main()

