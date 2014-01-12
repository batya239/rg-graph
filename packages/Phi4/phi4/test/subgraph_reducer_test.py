#!/usr/bin/python
# -*- coding: utf8
import copy
import unittest
import graphine
import const
import graph_state
import rggraphenv.graph_calculator as graph_calculator
import graphine.momentum as momentum
import gfun_calculator
import base_test_case
import reduction
import graph_util

# gfun_calculator.DEBUG = True


from_str = graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.graph_state_from_str


class SubGraphReducerTestCase(base_test_case.GraphStorageAwareTestCase):
    def testTadpole(self):
        state = from_str("ee11||:(0, 0)_(0, 0)_(1, 0)_(1, 0)||:")
        reducer = gfun_calculator.GGraphReducer(graphine.Graph(state))
        self.assertEqual(reducer.calculate(), ('0', graph_state.Rainbow((0, 0))))
    
    def test4LoopDiagram(self):
        g = graph_util.init_colors(graphine.Graph(from_str("e112|34|e33|4||")))
        reducer = gfun_calculator.GGraphReducer(g)
        reducer2 = copy.copy(reducer)
        while reducer.nextIteration():
            pass
        self.assertTrue(reducer.isSuccesfulDone())
        actual = str(reducer.getFinalValue()[0])
        self.assertEquals(reducer2.calculate(), reducer.getFinalValue())
        self.assertEquals(set(actual.split("*")), set("G(1, 1)*G(1, 1)*G(1, 2)*G(1, 4-l*3)".split("*")))
    
    def testPickPassingExternalMomentum(self):
        g = graphine.Graph(
            from_str("ee11|ee|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)_(0,0)|:"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)
    
        g = graphine.Graph(
            from_str("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|:"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)
    
        g = graphine.Graph(
            from_str("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|:"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)
    
        edges = list()
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((0, 1)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((0, 2)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((1, 2)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((1, 2)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 1)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 2)))
        g = graphine.Graph(
            graph_state.GraphState(edges))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 3)
    
    def testReducingEyeOfATiger(self):
        edges = list()
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((0, 1), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((0, 2), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 1), colors=(0, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 2), colors=(0, 0)))
        graph = graphine.Graph(
            graph_state.GraphState(edges))
        momentumPassing = (edges[-1], edges[0])
        res = gfun_calculator.GGraphReducer(graph, momentumPassing).calculate()
        self.assertEquals(res, ("G(1, 1)*G(1, 2-l*1)", graph_state.Rainbow((2, -2))))
    
    def testReducingE111_E_(self):
        graph = graph_util.init_colors(graphine.Graph(from_str("e111|e|")))
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G(1, 1)*G(1-l*1, 1)", graph_state.Rainbow((1, -2))))

    def testWithNumeratorsE11_E_(self):
        graph = graph_util.graph_from_str("e11|e|",
                                          do_init_color=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (0, 1)])
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G2(1, 1)", graph_state.Rainbow((0, -1))))

    def testWithNumerators1E11_E_(self):
        graph = graph_util.graph_from_str("e11|e|",
                                          do_init_color=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1)])
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(1, 1)", graph_state.Rainbow((1, -1))))

    def testWithNumerators(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_color=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(1, 0), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()
        self.assertEqual(res[1], graph_state.Rainbow((2, -2)))
        self.assertTrue("G1(2, 1)*G2(1, 3-l*1)" == res[0])

    def testWithNumerators2(self):
        graph = graph_util.graph_from_str("e12|e23|3||",
                                          do_init_color=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 1), (1, 3)])
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(2, 1)*(-G2(1, 3-l*1))", graph_state.Rainbow((2, -2))))

    def testWithNumerators3(self):
        graph = graph_util.graph_from_str("e12|e234|3|4||",
                                          do_init_color=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(1, 0), (1, 4)])
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(2, 1)*G1(3-l*1, 1)*G2(1, 4-l*2)", graph_state.Rainbow((3, -3))))

    def testWithNumerators4(self):
        gs = from_str(
            "e1123|2|3|e|:(0, 0)_(1, 0)_(2, 0)_(1, 0)_(1, 0)|(1, 0)|(2, -1)|(0, 0)|:0_0_>_0_<|0|0|0|")
        graph = graphine.Graph(gs)
        reducer = gfun_calculator.GGraphReducer(graph)
        reducer_calculate = reducer.calculate()
        self.assertTrue(reducer_calculate[0].count("-") % 2 == 1)

    def testWithNumerators5(self):
        graph = graph_util.graph_from_str("e112|34|3|e45|5|",
                                          do_init_color=True,
                                          do_init_arrow=True,
                                          arrow_lines=[(0, 2), (3, 5)])
        reducer = gfun_calculator.GGraphReducer(graph)
        res = reducer.calculate()

        self.assertEquals(res[1], graph_state.Rainbow((4, -4)))
        self.assertTrue(res[0].count("-") % 2 == 1)
    
    def testReducingE11_22_E_(self):
        graph = graph_util.init_colors(graphine.Graph(from_str("e11|22|e|")))
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(str(reducer.calculate()), "('G(1, 1)*G(1, 1)', (2, -2))")
    
    def testReducingE12_E23_33__(self):
        graph = graph_util.init_colors(graphine.Graph(from_str("e12|e23|33||")))
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(str(reducer.calculate()), "('G(1, 1)*G(1, 2-l*1)*G(1, 3-l*2)', (3, -3))")
    
    def testReducingAnotherDiagram(self):
        edges = list()
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((0, 1), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((0, 3), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((1, 3), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((2, 3), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((2, 3), colors=(1, 0)))
        edges.append(graph_state.COLORS_AND_ARROW_PROPERTIES_CONFIG.new_edge((-1, 3), colors=(0, 0)))
        graph = graphine.Graph(
            graph_state.GraphState(edges))
        momentumPassing = (edges[-1], edges[0])
        reducer = gfun_calculator.GGraphReducer(graph, momentumPassing)
        self.assertEquals(reducer.calculate(), ('G(1, 1)*G(1, 2-l*1)*G(1, 3-l*2)', graph_state.Rainbow((3, -3))))
    
    def testDiagramWithTBubbleLikeSubGraph(self):
        try:
            graph_calculator.addCalculator(reduction.TwoAndThreeReductionCalculator())
            g = graph_util.graph_from_str("e123|224|4|4|e|", do_init_color=True)
            reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
            self.assertIsNotNone(reducer.calculate())
        finally:
            graph_calculator.dispose()
    
    def testDiagramWithTBubbleLikeStructure(self):
        try:
            graph_calculator.addCalculator(reduction.TwoAndThreeReductionCalculator())
            g = graph_util.graph_from_str("e12|223|3|e|", do_init_color=True)
            reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
            self.assertIsNotNone(reducer.calculate())
        finally:
            graph_calculator.dispose()

    def assertIsNotNone(self, value):
        assert value is not None

    def assertIsNone(self, value):
        assert value is None

if __name__ == "__main__":
    unittest.main()