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


# noinspection PyMethodOverriding
class SubGraphReducerTestCase(base_test_case.GraphStorageAwareTestCase):
    def testTadpole(self):
        state = graphine.Graph.fromStr("ee11||:(0, 0)_(0, 0)_(1, 0)_(1, 0)||:")
        reducer = gfun_calculator.GGraphReducer(graphine.Graph.initEdgesColors(state))
        self.assertEqual(reducer.calculate(), ('0', (0, 0)))

    def test4LoopDiagram(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e112|34|e33|4||")))
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
            graph_state.GraphState.fromStr("ee11|ee|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)_(0,0)|:"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            graph_state.GraphState.fromStr("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|:"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            graph_state.GraphState.fromStr("e111|e|:(0,0)_(0,0)_(1, 0)_(1, 0)|(0,0)|:"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        edges = list()
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((0, 1)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((0, 2)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((1, 2)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((1, 2)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 1)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 2)))
        g = graphine.Graph(
            graph_state.GraphState(edges))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 3)

    def testReducingEyeOfATiger(self):
        edges = list()
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((0, 1), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((0, 2), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 1), colors=(0, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 2), colors=(0, 0)))
        graph = graphine.Graph(
            graph_state.GraphState(edges))
        momentumPassing = (edges[-1], edges[0])
        res = gfun_calculator.GGraphReducer(graph, momentumPassing).calculate()
        self.assertEquals(res, ("G(1, 1)*G(1, 2-l*1)", (2, -2)))

    def testReducingE111_E_(self):
        graph = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e111|e|")))
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G(1, 1)*G(1-l*1, 1)", (1, -2)))

    def testWithNumeratorsE11_E_(self):
        graph = graphine.Graph.fromStr("e11|e|",
                                       initEdgesColor=True,
                                       initFields=True,
                                       fieldLines=[(0, 1), (0, 1)],
                                       fieldValue=const.LEFT_NUMERATOR,
                                       noFieldValue=const.EMPTY_NUMERATOR)
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G2(1, 1)", (0, -1)))

    def testWithNumerators1E11_E_(self):
        graph = graphine.Graph.fromStr("e11|e|",
                                       initEdgesColor=True,
                                       initFields=True,
                                       fieldLines=[(0, 1)],
                                       fieldValue=const.LEFT_NUMERATOR,
                                       noFieldValue=const.EMPTY_NUMERATOR)
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(1, 1)", (1, -1)))

    def testWithNumerators(self):
        graph = graphine.Graph.fromStr("e12|e23|3||",
                                       initEdgesColor=True,
                                       initFields=True,
                                       fieldLines=[(1, 0), (1, 3)],
                                       fieldValue=const.LEFT_NUMERATOR,
                                       noFieldValue=const.EMPTY_NUMERATOR)
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(2, 1)*G2(1, 3-l*1)", (2, -2)))

    def testWithNumerators2(self):
        graph = graphine.Graph.fromStr("e12|e23|3||",
                                       initEdgesColor=True,
                                       initFields=True,
                                       fieldLines=[(0, 1), (1, 3)],
                                       fieldValue=const.LEFT_NUMERATOR,
                                       noFieldValue=const.EMPTY_NUMERATOR)
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(2, 1)*(-G2(1, 3-l*1))", (2, -2)))

    def testWithNumerators3(self):
        graph = graphine.Graph.fromStr("e12|e234|3|4||",
                                       initEdgesColor=True,
                                       initFields=True,
                                       fieldLines=[(1, 0), (1, 4)],
                                       fieldValue=const.LEFT_NUMERATOR,
                                       noFieldValue=const.EMPTY_NUMERATOR)
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(reducer.calculate(), ("G1(2, 1)*G1(3-l*1, 1)*G2(1, 4-l*2)", (3, -3)))

    def testReducingE11_22_E_(self):
        graph = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11|22|e|")))
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(str(reducer.calculate()), "('G(1, 1)*G(1, 1)', (2, -2))")

    def testReducingE12_E23_33__(self):
        graph = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e12|e23|33||")))
        reducer = gfun_calculator.GGraphReducer(graph)
        self.assertEquals(str(reducer.calculate()), "('G(1, 1)*G(1, 2-l*1)*G(1, 3-l*2)', (3, -3))")

    def testReducingAnotherDiagram(self):
        edges = list()
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((0, 1), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((0, 3), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((1, 3), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((2, 3), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((2, 3), colors=(1, 0)))
        edges.append(graph_state.DEFAULT_PROPERTIES_CONFIG.new_edge((-1, 3), colors=(0, 0)))
        graph = graphine.Graph(
            graph_state.GraphState(edges))
        momentumPassing = (edges[-1], edges[0])
        reducer = gfun_calculator.GGraphReducer(graph, momentumPassing)
        self.assertEquals(reducer.calculate(), ('G(1, 1)*G(1, 2-l*1)*G(1, 3-l*2)', (3, -3)))

    # def testDiagramWithTBubbleLikeSubGraph(self):
    #     try:
    #         graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
    #         g = graphine.Graph.fromStr("e123-224-4-4-e-", initEdgesColor=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         self.assertIsNotNone(reducer.calculate())
    #     finally:
    #         graph_calculator.dispose()
    # 
    # def testDiagramWithTBubbleLikeStructure(self):
    #     try:
    #         graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
    #         g = graphine.Graph.fromStr("e12-223-3-e-::", initEdgesColor=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         self.assertIsNotNone(reducer.calculate())
    #     finally:
    #         graph_calculator.dispose()
    # 
    # def testDiagram5Loops(self):
    #     try:
    #         graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
    #         g = graphine.Graph.fromStr("e1123-34-34-e--", initEdgesColor=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         calculated = reducer.calculate()
    #         print calculated
    #         print symbolic_functions.series(symbolic_functions.evaluate(calculated[0]), symbolic_functions.e, 0, 0).simplify_indexed().evalf()
    #         self.assertIsNotNone(calculated)
    #     finally:
    #         graph_calculator.dispose()
    # 
    # def testDiagram5Loops2(self):
    #     try:
    #         graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
    #         g = graphine.Graph.fromStr("e12-e234-35-45-5--", initEdgesColor=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         calculated = reducer.calculate()
    #         print calculated
    #         print symbolic_functions.series(symbolic_functions.evaluate(calculated[0]), symbolic_functions.e, 0, 0).simplify_indexed().evalf()
    #         self.assertIsNotNone(calculated)
    #     finally:
    #         graph_calculator.dispose()
    # 
    # def testDiagramWithTBubbleLikeStructure2(self):
    #     try:
    #         graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
    #         g = graphine.Graph.fromStr("e123-e23-33--::", initEdgesColor=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         self.assertIsNotNone(reducer.calculate())
    #     finally:
    #         graph_calculator.dispose()
    # 
    # def testDiagram5LoopsNotCalculated(self):
    #     try:
    #         graph_calculator.addCalculator(mincer_graph_calculator.MincerGraphCalculator())
    #         g = graphine.Graph.fromStr("e112-34-345-e-55--", initEdgesColor=True)
    #         reducer = gfun_calculator.GGraphReducer(g, useGraphCalculator=True)
    #         self.assertIsNone(reducer.calculate())
    #     finally:
    #         # graph_calculator.dispose()

    def assertIsNotNone(self, value):
        assert value is not None

    def assertIsNone(self, value):
        assert value is None

if __name__ == "__main__":
    unittest.main()