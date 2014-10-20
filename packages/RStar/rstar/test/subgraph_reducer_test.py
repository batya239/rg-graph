#!/usr/bin/python
# -*- coding: utf8
import copy
import unittest
import graphine
import graph_state
import reduction
import time
import inject

import const
import graph_util
import momentum
import common
import ir_uv
import rggraphenv
import gfun_calculator
import numerators_util
import configure
from rggraphutil import VariableAwareNumber
from rggraphenv import symbolic_functions, g_graph_calculator, StorageHolder, StorageSettings


gfun_calculator.DEBUG = True

from_str = graph_util.graph_from_str
new_edge = graph_util.new_edge
G, G1, G2, l, e = symbolic_functions.G, symbolic_functions.G1, symbolic_functions.G2, symbolic_functions.l, symbolic_functions.e


class SubGraphReducerTestCase(unittest.TestCase):
    holder = None
    time = None

    def setUp(self):
        configure.Configure()\
            .with_k_operation(common.MSKOperation())\
            .with_ir_filter(ir_uv.IRRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_uv_filter(ir_uv.UVRelevanceCondition(const.SPACE_DIM_PHI4))\
            .with_dimension(const.DIM_PHI4)\
            .with_calculators(g_graph_calculator.GLoopCalculator(const.DIM_PHI4))\
            .with_storage_holder(StorageSettings("phi4", "test", "test", test=True)).configure()
        SubGraphReducerTestCase.time = time.time()

    def tearDown(self):
        StorageHolder.instance().close()
        configure.Configure.clear()
        t = time.time() - SubGraphReducerTestCase.time
        print "SUMMARY TIME : %.3f" % t

    def testTadpole(self):
        graph = from_str("ee11||:(0, 0)_(0, 0)_(1, 0)_(1, 0)||:::")
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertEqual((res[0].get(), res[1]), (0, VariableAwareNumber("l", 0)))

    def test4LoopDiagram(self):
        g = graph_util.init_weight(from_str("e112|34|e33|4||"))
        reducer = gfun_calculator.GGraphReducer(g)
        actual = reducer.calculate()
        self.assertTrue(actual[0].is_equal(G(1, 1) * G(1, 1) * G(1, 2) * G(1, 4 - l * 3)), actual)
        self.assertEqual(actual[1], VariableAwareNumber("l", 4, -4))

    def testPickPassingExternalMomentum(self):
        g = from_str("ee11|ee|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)_(0,0)|:::")
        passings = [x for x in momentum.x_pick_passing_external_momentum(g)]
        self.assertEquals(len(passings), 1)

        g = from_str("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|:::")
        passings = [x for x in momentum.x_pick_passing_external_momentum(g)]
        self.assertEquals(len(passings), 1)

        g = from_str("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|:::")
        passings = [x for x in momentum.x_pick_passing_external_momentum(g)]
        self.assertEquals(len(passings), 1)

        edges = list()
        edges.append(new_edge((-1, 0)))
        edges.append(new_edge((-1, 0)))
        edges.append(new_edge((0, 1)))
        edges.append(new_edge((0, 2)))
        edges.append(new_edge((1, 2)))
        edges.append(new_edge((1, 2)))
        edges.append(new_edge((-1, 1)))
        edges.append(new_edge((-1, 2)))
        g = graphine.Graph(
            graph_state.GraphState(edges))
        passings = [x for x in momentum.x_pick_passing_external_momentum(g)]
        self.assertEquals(len(passings), 3)

    def testReducingE111_E_(self):
        graph = graph_util.init_weight(from_str("e111|e|"))
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G(1, 1) * G(1 - l * 1, 1)))
        self.assertEquals(res[1], VariableAwareNumber("l", 1, -2))

    def testWithNumeratorsE11_E_(self):
        graph = graph_util.graph_from_str("e11|e|",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (0, 1)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G2(1, 1)))
        self.assertEquals(res[1], VariableAwareNumber("l", 0, -1))

    def _testWithNumerators1E11_E_(self):
        """
        now this test is crashed
        """
        graph = graph_util.graph_from_str("e11|e|",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1)])
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(1, 1)", graph_state.Rainbow((1, -1))))

    def testWithNumerators(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(1, 0), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertEqual(res[1], VariableAwareNumber("l", 2, -2))
        self.assertTrue(res[0].is_equal(G1(2, 1) * G2(1, 3 - l * 1)))

    def testWithNumerators2(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G1(2, 1) * (-G2(1, 3 - l * 1))))
        self.assertEquals(res[1], VariableAwareNumber("l", 2, -2))

    def testWithNumerators22(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G1(2, 1) * (-G2(1, 3 - l * 1))))
        self.assertEquals(res[1], VariableAwareNumber("l", 2, -2))

    def testWithNumerators33(self):
        graph = graph_util.graph_from_str("e12|e2||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 2), (2, 1)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G(1, 1)))
        self.assertEquals(res[1], VariableAwareNumber("l", 1, -1))

    def testWithNumerators3(self):
        graph = graph_util.graph_from_str("e12|e234|3|4||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(1, 0), (1, 4)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G1(2, 1) * G1(3 - l * 1, 1) * G2(1, 4 - l * 2)))
        self.assertEquals(res[1], VariableAwareNumber("l", 3, -3))

    def testWithNumerators5(self):
        graph = graph_util.graph_from_str("e112|34|3|e45|5|",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 2), (3, 5)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()

        self.assertEquals(res[1], VariableAwareNumber("l", 4, -4))
        self.assertTrue(res[0].is_equal(-G1(2, 1) * G(1, 1) * G1(3 - l, 1) * G2(4 - 3 * l, 2)))

    def testWithNumerators7(self):
        graph = graph_util.graph_from_str(
            "e123|e24|34|||:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(0, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|||:0_0_0_0|0_0_0|<_<|||:None_None_None_1|None_None_1|1_1|||:")
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertEquals(res[1], VariableAwareNumber("l", 3, -3))
        self.assertTrue(res[0].is_equal(-G1(2,1)**2*G(1+2*e,1)))

    def testWithNumerators6(self):
        graph = graph_util.graph_from_str(
            "e112|33|e4|45|56|6||:(0, 0)_(1, 0)_(1, 0)_(1, 0)|(1, 0)_(1, 0)|(0, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)_(1, 0)|(1, 0)||:0_0_0_0|0_0|0_>|0_0|0_0|<||:None_None_None_1|None_None|None_1|None_None|None_1|1||:")
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertEquals(res[1], VariableAwareNumber("l", 5, -5))
        self.assertTrue(res[0].is_equal(G(1, 1) ** 2 * G1(2, 1) * G1(3 - l, 1) * G(5 - 4 * l, 1)))

    def testReducingE11_22_E_(self):
        graph = graph_util.init_weight(from_str("e11|22|e|"))
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G(1, 1) * G(1, 1)))
        self.assertEqual(res[1], VariableAwareNumber("l", 2, -2))

    def testReducingE12_E23_33__(self):
        graph = graph_util.init_weight(from_str("e12|e23|33||"))
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G(1, 1) * G(1, 2 - l * 1) * G(1, 3 - l * 2)))
        self.assertEqual(res[1], VariableAwareNumber("l", 3, -3))

    def testReducingAnotherDiagram(self):
        edges = list()
        edges.append(new_edge((-1, 0),
                                                                                    weight=VariableAwareNumber("l", 0,
                                                                                                               0)))
        edges.append(new_edge((0, 1),
                                                                                    weight=VariableAwareNumber("l", 1,
                                                                                                               0)))
        edges.append(new_edge((0, 3),
                                                                                    weight=VariableAwareNumber("l", 1,
                                                                                                               0)))
        edges.append(new_edge((1, 2),
                                                                                    weight=VariableAwareNumber("l", 1,
                                                                                                               0)))
        edges.append(new_edge((1, 3),
                                                                                    weight=VariableAwareNumber("l", 1,
                                                                                                               0)))
        edges.append(new_edge((2, 3),
                                                                                    weight=VariableAwareNumber("l", 1,
                                                                                                               0)))
        edges.append(new_edge((2, 3),
                                                                                    weight=VariableAwareNumber("l", 1,
                                                                                                               0)))
        edges.append(new_edge((-1, 3),
                                                                                    weight=VariableAwareNumber("l", 0,
                                                                                                               0)))
        graph = graphine.Graph(graph_state.GraphState(edges))
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G(1, 1) * G(1, 2 - l * 1) * G(1, 3 - l * 2)))
        self.assertEqual(res[1], VariableAwareNumber("l", 3, -3))

    def assertIsNotNone(self, value):
        assert value is not None

    def assertIsNone(self, value):
        assert value is None


if __name__ == "__main__":
    unittest.main()