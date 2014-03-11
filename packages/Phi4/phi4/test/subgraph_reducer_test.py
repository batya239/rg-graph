#!/usr/bin/python
# -*- coding: utf8
import copy
import unittest
import graphine
import const
import graph_state
import graphine.momentum as momentum
import rggraphenv
import gfun_calculator
import reduction
import graph_util
import numerators_util
import time
import inject
from rggraphutil import VariableAwareNumber
from rggraphenv import symbolic_functions

gfun_calculator.DEBUG = True


from_str = graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.graph_state_from_str
G, G1, G2, l = symbolic_functions.G, symbolic_functions.G1, symbolic_functions.G2, symbolic_functions.l


class SubGraphReducerTestCase(unittest.TestCase):
    holder = None
    time = None

    @classmethod
    def setUpClass(cls):
        def config(binder):
            binder.bind(rggraphenv.StoragesHolder, rggraphenv.StoragesHolder(rggraphenv.StorageSettings("phi4", "test", "test").on_shutdown(revert=True)))
            binder.bind(rggraphenv.GraphCalculatorManager, rggraphenv.GraphCalculatorManager(rggraphenv.GLoopCalculator(dimension=symbolic_functions.d_phi4)))
        inject.configure(config)
        SubGraphReducerTestCase.time = time.time()

    @classmethod
    def tearDownClass(cls):
        inject.instance(rggraphenv.StoragesHolder).close(revert=True)
        t = time.time() - SubGraphReducerTestCase.time
        print "SUMMARY TIME : %.3f" % t

    def testTadpole(self):
        state = from_str("ee11||:(0, 0)_(0, 0)_(1, 0)_(1, 0)||::")
        reducer = gfun_calculator.GGraphReducer(graphine.Graph(state))
        res = reducer.calculate()
        self.assertEqual((res[0].get(), res[1]) , (0, VariableAwareNumber("l", 0)))

    def test4LoopDiagram(self):
        g = graph_util.init_weight(graphine.Graph(from_str("e112|34|e33|4||")))
        reducer = gfun_calculator.GGraphReducer(g)
        actual = reducer.calculate()
        self.assertTrue(actual[0].is_equal(G(1, 1)*G(1, 1)*G(1, 2)*G(1, 4-l*3)), actual)
        self.assertEqual(actual[1], VariableAwareNumber("l", 4, -4))

    def testPickPassingExternalMomentum(self):
        g = graphine.Graph(
            from_str("ee11|ee|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)_(0,0)|::"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            from_str("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|::"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            from_str("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|::"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        edges = list()
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((-1, 0)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((-1, 0)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((0, 1)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((0, 2)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((1, 2)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((1, 2)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((-1, 1)))
        edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((-1, 2)))
        g = graphine.Graph(
            graph_state.GraphState(edges))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 3)

    def testReducingE111_E_(self):
        graph = graph_util.init_weight(graphine.Graph(from_str("e111|e|")))
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G(1, 1)*G(1-l*1, 1)))
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
        self.assertTrue(res[0].is_equal(G1(2, 1)*G2(1, 3-l*1)))

    def testWithNumerators2(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G1(2, 1)*(-G2(1, 3-l*1))))
        self.assertEquals(res[1], VariableAwareNumber("l", 2, -2))

    def testWithNumerators22(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_weight=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertTrue(res[0].is_equal(G1(2, 1)*(-G2(1, 3-l*1))))
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
        self.assertTrue(res[0].is_equal(G1(2, 1)*G1(3-l*1, 1)*G2(1, 4-l*2)))
        self.assertEquals(res[1], VariableAwareNumber("l", 3, -3))

    # def testWithNumerators4(self):
    #     graph_calculator.addCalculator(numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)
    #     gs = graph_util.graph_from_str(
    #         "e1123|24|5|e46|56|||", do_init_arrow=True, do_init_weight=True, arrow_lines=[(3, 6), (4, 5)])
    #     graph = gs
    #     reducer = gfun_calculator.GGraphReducer(graph)
    #     reducer_calculate = reducer.calculate()
    #     print "VALUE", reducer_calculate
    #
    # def testWithNumerators5(self):
    #     graph = graph_util.graph_from_str("e112|34|3|e45|5|",
    #                                       do_init_weight=True,
    #                                       do_init_arrow=True,
    #                                       arrow_lines=[(0, 2), (3, 5)])
    #     reducer = gfun_calculator.GGraphReducer(graph)
    #     res = reducer.calculate()
    #
    #     self.assertEquals(res[1], graph_state.Rainbow((4, -4)))
    #     self.assertTrue(res[0].count("-") % 2 == 1)
    #
    # def testReducingE11_22_E_(self):
    #     graph = graph_util.init_weight(graphine.Graph(from_str("e11|22|e|")))
    #     reducer = gfun_calculator.GGraphReducer(graph)
    #     self.assertEquals(str(reducer.calculate()), "('G(1, 1)*G(1, 1)', (2, -2))")
    #
    # def testReducingE12_E23_33__(self):
    #     graph = graph_util.init_weight(graphine.Graph(from_str("e12|e23|33||")))
    #     reducer = gfun_calculator.GGraphReducer(graph)
    #     self.assertEquals(str(reducer.calculate()), "('G(1, 1)*G(1, 2-l*1)*G(1, 3-l*2)', (3, -3))")
    
    # def testReducingAnotherDiagram(self):
    #     edges = list()
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((-1, 0), weight=(0, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((0, 1), weight=(1, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((0, 3), weight=(1, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((1, 2), weight=(1, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((1, 3), weight=(1, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((2, 3), weight=(1, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((2, 3), weight=(1, 0)))
    #     edges.append(graph_state.WEIGHT_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge((-1, 3), weight=(0, 0)))
    #     graph = graphine.Graph(
    #         graph_state.GraphState(edges))
    #     momentumPassing = (edges[-1], edges[0])
    #     reducer = gfun_calculator.GGraphReducer(graph, momentumPassing)
    #     self.assertEquals(reducer.calculate(), ('G(1, 1)*G(1, 2-l*1)*G(1, 3-l*2)', graph_state.Rainbow((3, -3))))
    #
    # def testDiagramWithTBubbleLikeSubGraph(self):
    #     try:
    #         graph_calculator.addCalculator(reduction.ReductionGraphCalculator())
    #         g = graph_util.graph_from_str("e123|224|4|4|e|", do_init_weight=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         self.assertIsNotNone(reducer.calculate())
    #     finally:
    #         graph_calculator.dispose()

    # def testDiagramWithTBubbleLikeStructure(self):
    #     try:
    #         graph_calculator.addCalculator(numerators_util.GRAPHS_WITH_SCALAR_PRODUCTS_CALCULATOR)
    #         g = graph_util.graph_from_str("e1123|e45|445|46||6||", do_init_weight=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         res = reducer.calculate()
    #         print res
    #         self.assertIsNotNone(res)
    #     finally:
    #         graph_calculator.dispose()

    def assertIsNotNone(self, value):
        assert value is not None

    def assertIsNone(self, value):
        assert value is None

if __name__ == "__main__":
    unittest.main()