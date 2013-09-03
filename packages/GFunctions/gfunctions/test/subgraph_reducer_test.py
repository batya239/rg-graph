#!/usr/bin/python
# -*- coding: utf8
import copy
import unittest
import graphine
import graph_state
import mincer_adapter
import graph_calculator
import momentum
import subgraph_processer
import test


class SubGraphReducerTestCase(test.GraphStorageAwareTestCase):
    def test4LoopDiagram(self):
        g = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e112-34-e33-4--::")))
        reducer = subgraph_processer.GGraphReducer(g)
        reducer2 = copy.copy(reducer)
        while reducer.nextIteration():
            pass
        self.assertTrue(reducer.isSuccesfulDone())
        actual = str(reducer.getFinalValue()[0])
        self.assertEquals(reducer2.calculate(), reducer.getFinalValue())
        self.assertEquals(set(actual.split("*")), set("G(1, 1)*G(1, 1)*G(1, 2)*G(1, 4-lambda*3)".split("*")))

    def testPickPassingExternalMomentum(self):
        g = graphine.Graph(
            graph_state.GraphState.fromStr("ee11-ee-::['(0,0)', '(0,0)', '(1, 0)', '(1, 0)', '(0,0)', '(0,0)']"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            graph_state.GraphState.fromStr("e111-e-::['(0,0)', '(0,0)', '(1, 0)', '(1, 0)', '(0,0)']"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            graph_state.GraphState.fromStr("e111-e-::['(0,0)', '(0,0)', '(1, 0)', '(1, 0)', '(0,0)']"))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        edges = list()
        edges.append(graph_state.Edge((-1, 0)))
        edges.append(graph_state.Edge((-1, 0)))
        edges.append(graph_state.Edge((0, 1)))
        edges.append(graph_state.Edge((0, 2)))
        edges.append(graph_state.Edge((1, 2)))
        edges.append(graph_state.Edge((1, 2)))
        edges.append(graph_state.Edge((-1, 1)))
        edges.append(graph_state.Edge((-1, 2)))
        g = graphine.Graph(
            graph_state.GraphState(edges))
        passings = [x for x in momentum.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 5)

    def testReducingEyeOfATiger(self):
        edges = list()
        edges.append(graph_state.Edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.Edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.Edge((0, 1), colors=(1, 0)))
        edges.append(graph_state.Edge((0, 2), colors=(1, 0)))
        edges.append(graph_state.Edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.Edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.Edge((-1, 1), colors=(0, 0)))
        edges.append(graph_state.Edge((-1, 2), colors=(0, 0)))
        graph = graphine.Graph(
            graph_state.GraphState(edges))
        momentumPassing = (edges[-1], edges[0])
        reducer = subgraph_processer.GGraphReducer(graph, momentumPassing)
        reducer2 = copy.copy(reducer)
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e12-e2--::['(0, 0)', '(1, 0)', '(1, -1)', '(0, 0)', '(1, 0)']")
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e11-e-::['(0, 0)', '(1, 0)', '(2, -1)', '(0, 0)']")
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e1-e-::['(0, 0)', '(2, -2)', '(0, 0)']")
        hasIteration = reducer.nextIteration()
        self.assertFalse(hasIteration)
        self.assertEquals(reducer2.calculate(), reducer.getFinalValue())


    def testReducingE111_E_(self):
        graph = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e111-e-::")))
        reducer = subgraph_processer.GGraphReducer(graph)
        reducer2 = copy.copy(reducer)
        self.assertTrue(reducer.nextIteration())
        self.assertTrue(reducer.nextIteration())
        self.assertTrue(reducer.isSuccesfulDone())
        self.assertEquals(reducer2.calculate(), reducer.getFinalValue())

    def testReducingE11_22_E_(self):
        graph = graphine.Graph.initEdgesColors(graphine.Graph(graph_state.GraphState.fromStr("e11-22-e-::")))
        reducer = subgraph_processer.GGraphReducer(graph)
        reducer2 = copy.copy(reducer)
        self.assertTrue(reducer.nextIteration())
        self.assertTrue(reducer.nextIteration())
        self.assertTrue(reducer.nextIteration())
        self.assertTrue(reducer.isSuccesfulDone())
        self.assertEquals("('G(1, 1)*G(1, 1)', (2, -2))", str(reducer.getFinalValue()))
        self.assertEquals(reducer2.calculate(), reducer.getFinalValue())


    def testReducingAnotherDiagram(self):
        edges = list()
        edges.append(graph_state.Edge((-1, 0), colors=(0, 0)))
        edges.append(graph_state.Edge((0, 1), colors=(1, 0)))
        edges.append(graph_state.Edge((0, 3), colors=(1, 0)))
        edges.append(graph_state.Edge((1, 2), colors=(1, 0)))
        edges.append(graph_state.Edge((1, 3), colors=(1, 0)))
        edges.append(graph_state.Edge((2, 3), colors=(1, 0)))
        edges.append(graph_state.Edge((2, 3), colors=(1, 0)))
        edges.append(graph_state.Edge((-1, 3), colors=(0, 0)))
        graph = graphine.Graph(
            graph_state.GraphState(edges))
        momentumPassing = (edges[-1], edges[0])
        reducer = subgraph_processer.GGraphReducer(graph, momentumPassing)
        reducer2 = copy.copy(reducer)
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e12-e23-3--::['(0, 0)', '(1, 0)', '(1, 0)', '(0, 0)', '(1, 0)', '(1, -1)', '(1, 0)']")
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e112-2-e-::['(0, 0)', '(1, 0)', '(2, -1)', '(1, 0)', '(1, 0)', '(0, 0)']")
        self.assertEquals(reducer2.calculate(), ('G(1, 1)*G(1, 2-lambda*1)*G(1, 3-lambda*2)', graph_state.Rainbow((3, -3))))

    def testDiagramWithTBubbleLikeStructure(self):
        try:
            graph_calculator.addCalculator(mincer_adapter.MincerGraphCalculator())
            g = graphine.Graph.fromStr("e12-223-3-e-::", initEdgesColor=True)
            reducer = subgraph_processer.GGraphReducer(g, useGraphCalculator=True)
            reducer2 = copy.copy(reducer)

            while reducer.nextIteration():
                pass
            self.assertTrue(reducer.isSuccesfulDone())
            self.assertEquals(reducer2.calculate(), reducer.getFinalValue())
        finally:
            graph_calculator.dispose()

if __name__ == "__main__":
    unittest.main()


