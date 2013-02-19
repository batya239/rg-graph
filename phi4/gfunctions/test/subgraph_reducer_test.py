import unittest
import graphine
import subgraph_processer

__author__ = 'dima'

import graph_state


class SubGraphReducerTestCase(unittest.TestCase):
    def testPickPassingExternalMomentum(self):
        g = graphine.Graph(
            graph_state.GraphState.fromStr("ee11-ee-::['(0,0)', '(0,0)', '(1, 0)', '(1, 0)', '(0,0)', '(0,0)']"))
        passings = [x for x in subgraph_processer.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 4)

        g = graphine.Graph(
            graph_state.GraphState.fromStr("e111-e-::['(0,0)', '(0,0)', '(1, 0)', '(1, 0)', '(0,0)']"))
        passings = [x for x in subgraph_processer.xPickPassingExternalMomentum(g)]
        self.assertEquals(len(passings), 1)

        g = graphine.Graph(
            graph_state.GraphState.fromStr("e111-e-::['(0,0)', '(0,0)', '(1, 0)', '(1, 0)', '(0,0)']"))
        passings = [x for x in subgraph_processer.xPickPassingExternalMomentum(g)]
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
        passings = [x for x in subgraph_processer.xPickPassingExternalMomentum(g)]
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
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e12-e23-3--::['(0, 0)', '(1, 0)', '(1, 0)', '(0, 0)', '(1, 0)', '(1, -1)', '(1, 0)']")
        hasIteration = reducer.nextIteration()
        self.assertTrue(hasIteration)
        self.assertEquals(str(reducer.getCurrentIterationGraph().toGraphState()),
                          "e112-2-e-::['(0, 0)', '(1, 0)', '(2, -1)', '(1, 0)', '(1, 0)', '(0, 0)']")

if __name__ == "__main__":
    unittest.main()


