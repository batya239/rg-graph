#!/usr/bin/python
# -*- coding: utf8
import copy
import graphine
import graph_state
import common
import lambda_number
import const
from rggraphenv import storage, graph_calculator, symbolic_functions

DEBUG = False
new_edge = graph_state.COLORS_ARROW_AND_MARKER_PROPERTIES_CONFIG.new_edge


def _create_filter():
    class RelevanceCondition:
    # noinspection PyUnusedLocal
        def __init__(self):
            pass

        # noinspection PyUnusedLocal
        def isRelevant(self, edgesList, superGraph, superGraphEdges):
            subGraph = graphine.Representator.asGraph(edgesList, superGraph.externalVertex)
            vertexes = set()
            for e in subGraph.edges(superGraph.externalVertex):
                vertexes |= set(e.nodes)
                # external node and 2 internals
            return len(vertexes) == 3

    return graphine.filters.oneIrreducible + graphine.filters.isRelevant(
        RelevanceCondition())

_FILTER = _create_filter()


def calculateGraphsValues(graphs, suppressException=False, useGraphCalculator=False):
    return reduce(lambda e, g: e * calculateGraphValue(g, suppressException, useGraphCalculator=useGraphCalculator)[0],
                  graphs, 1)


def calculateGraphValue0(graph, suppressException=False, useGraphCalculator=False):
    return calculateGraphValue(graph, suppressException, useGraphCalculator)[0]


def calculateGraphValue(graph, suppressException=False, useGraphCalculator=False):
    if len(graph.edges(graph.externalVertex)) == 2:
        graphReducer = GGraphReducer(graph, useGraphCalculator=useGraphCalculator)
    else:
        graphReducer = None
        for g in graphine.momentum.xPassExternalMomentum(graph, common.defaultGraphHasNotIRDivergenceFilter):
            graphReducer = GGraphReducer(g, useGraphCalculator=useGraphCalculator)
            break
        if graphReducer is None:
            raise common.CannotBeCalculatedError(graph)
    result = graphReducer.calculate()
    if not result:
        if suppressException:
            return None
        else:
            raise common.CannotBeCalculatedError(graph)
    evaluated = symbolic_functions.evaluate(result[0], result[1])
    return evaluated, graphReducer.iterationGraphs[0]


def _adjust(graphAsList, externalVertex):
    adjustedEdges = []
    boundaryVertexes = list()
    boundaryEdges = list()
    adjustedExternalEdges = []
    has_arrows = graphAsList[0].arrow is not None
    for e in graphAsList:
        if externalVertex in e.nodes:
            if e.internal_nodes[0] not in boundaryVertexes:
                boundaryVertexes.append(e.internal_nodes[0])
                boundaryEdges.append(e)

        else:
            adjustedEdges.append(e)
    for e, _id in zip(boundaryEdges, (GGraphReducer.START_ID, GGraphReducer.END_ID)):
        adjustedExternalEdges.append(e.copy(colors=graph_state.Rainbow((_id, 0)) if has_arrows else graph_state.Rainbow((0, 0)),
                                            arrow=graph_state.Arrow(graph_state.Arrow.NULL) if has_arrows else None))
    return adjustedEdges + adjustedExternalEdges, adjustedEdges, (tuple(boundaryVertexes))


class GGraphReducer(object):
    START_ID = 666
    END_ID = 777
    DEBUG = False

    @staticmethod
    def setDebug(debug):
        GGraphReducer.DEBUG = debug

    def __init__(self,
                 graph,
                 momentumPassing=list(),
                 subGraphFilters=list(),
                 rawFilters=False,
                 useGraphCalculator=False,
                 iterationGraphs=None,
                 iterationValues=None,
                 used_arrows=list()):
        """
        momentumPassing -- two external edges of graph in which external momentum passing
        """
        graph_str = str(graph)
        self._arrows_aware = ":" in graph_str and len(graph_str.split(":")[2]) != 0
        if isinstance(graph, graphine.Graph):
            if len(momentumPassing):
                self._initGraph = graphine.momentum.passMomentOnGraph(graph, momentumPassing)
            else:
                self._initGraph = graph
        else:
            raise TypeError('unsupported type of initial graph %s' % type(graph))
        self._iterationGraphs = [self._initGraph] if iterationGraphs is None else iterationGraphs
        self._iterationValues = [] if iterationValues is None else iterationValues
        self._subGraphFilter = subGraphFilters if rawFilters else (_FILTER + subGraphFilters)
        self._useGraphCalculator = useGraphCalculator
        self._isTadpole = None
        self._used_arrows = used_arrows

    @property
    def iterationValues(self):
        return self._iterationValues

    @property
    def iterationGraphs(self):
        return self._iterationGraphs

    @property
    def externalVertex(self):
        return self._initGraph.externalVertex

    @property
    def iterationsCount(self):
        return len(self._iterationValues)

    def getCurrentIterationGraph(self):
        return self._iterationGraphs[-1]

    def getCurrentIterationValue(self):
        return self._iterationValues[-1] if len(self._iterationValues) else None

    def isSuccesfulDone(self):
        return len(self.getCurrentIterationGraph().allEdges()) == 3 and ("<" not in str(self.getCurrentIterationGraph()) and ">" not in str(self.getCurrentIterationGraph()))

    def calculate(self):
        """
        find chain or maximal known subgraph and shrink it
        return True if has nextIteration or False if not
        """
        lastIteration = self.getCurrentIterationGraph()
        if self._isTadpole is None:
            self._isTadpole = str(lastIteration).startswith("ee")
            if self._isTadpole:
                return "0", graph_state.Rainbow((0, 0))

        if (len(lastIteration.allEdges()) == 3 and ("<" not in str(self.getCurrentIterationGraph()) and ">" not in str(self.getCurrentIterationGraph()))) or str(lastIteration).startswith("ee"):
            self._putFinalValueToGraphStorage()
            if DEBUG:
                print "CALCULATED_GRAPH", self._initGraph, self.iterationGraphs, self.iterationValues
            return self.getFinalValue()

        res_red = self._tryReduceChain2()
        if res_red is not None:
            return res_red

        relevant_sub_graphs = [x for x in
                               lastIteration.xRelevantSubGraphs(self._subGraphFilter,
                                                                graphine.Representator.asList)] + \
                              [lastIteration.allEdges()]
        relevant_sub_graphs = relevant_sub_graphs[::-1]
        relevant_sub_graphs.sort(lambda y, x: - len(y) + len(x))

        cached_preprocessed_subgraphs = list()
        for subGraphAsList in relevant_sub_graphs:
            adjustedSubGraph = _adjust(subGraphAsList, self._initGraph.externalVertex)
            subGraph = graphine.Graph(adjustedSubGraph[0],
                                      externalVertex=self._initGraph.externalVertex)
            preprocessed = (adjustedSubGraph[1], subGraph, adjustedSubGraph[2])
            cached_preprocessed_subgraphs.append(preprocessed)
            if storage.hasGraph(subGraph):
                if DEBUG:
                    print "sg", subGraph, lastIteration
                res = self._do_iterate(preprocessed)
                if res is not None:
                    return res

        if self._useGraphCalculator:
            for preprocessed in cached_preprocessed_subgraphs:
                    if self._arrows_aware:
                        _as = filter(lambda e: not e.arrow.is_null(), preprocessed[1].allEdges())
                        if len(_as) % 2 == 0:
                            can_calculate = len(self._used_arrows) == 0
                        else:
                            assert len(_as) == 1
                            can_calculate = True
                    else:
                        can_calculate = True
                    if can_calculate:
                        result = graph_calculator.tryCalculate(preprocessed[1], putValueToStorage=True)
                        if result is not None:
                            res = self._do_iterate(preprocessed)
                            if res is not None:
                                return res

    def _do_iterate(self, sub_graph_info):
        assert len(sub_graph_info[2]) == 2, sub_graph_info[2]
        new_iteration = self.getCurrentIterationGraph()
        iter_sub_graph_value = storage.getGraph(sub_graph_info[1])

        new_used_arrows = copy.copy(self._used_arrows)
        for a in self._used_arrows:
            if a in sub_graph_info[0]:
                new_used_arrows.remove(a)
        if self._arrows_aware:
            _as = filter(lambda e: not e.arrow.is_null(), sub_graph_info[1].allEdges())
            if len(_as) % 2 == 0:
                arrow = graph_state.Arrow(graph_state.Arrow.NULL)
            else:
                arrow = graph_state.Arrow(graph_state.Arrow.LEFT_ARROW) if sub_graph_info[1].allEdges(nickel_ordering=True)[0].colors[0] == GGraphReducer.START_ID else graph_state.Arrow(graph_state.Arrow.RIGHT_ARROW)
        else:
            arrow = None

        edge = new_edge(sub_graph_info[2],
                        self._initGraph.externalVertex,
                        colors=graph_state.Rainbow(iter_sub_graph_value[0][1]),
                        arrow=arrow,
                        const=const.MARKER_0 if arrow is None else const.MARKER_1)

        if edge.arrow is not None and not edge.arrow.is_null():
            new_used_arrows.append(edge)

        new_iteration = new_iteration.change(sub_graph_info[0], [edge])

        new_iteration_graphs = copy.copy(self._iterationGraphs)
        new_iteration_graphs.append(new_iteration)
        new_iteration_values = copy.copy(self._iterationValues)
        new_iteration_values.append(iter_sub_graph_value[0][0])

        new_reducer = GGraphReducer(self._initGraph,
                                    useGraphCalculator=self._useGraphCalculator,
                                    rawFilters=True,
                                    subGraphFilters=self._subGraphFilter,
                                    iterationGraphs=new_iteration_graphs,
                                    iterationValues=new_iteration_values,
                                    used_arrows=new_used_arrows)

        return new_reducer.calculate()

    def _tryReduceChain2(self):
        edgesAndVertex = self._searchForChains()
        if not edgesAndVertex:
            return None
        else:
            edges, v = edgesAndVertex
            assert len(edges) == 2
            boundaryVertexes = []
            new_lambda_number = None
            for e in edges:
                if not new_lambda_number:
                    new_lambda_number = lambda_number.from_rainbow(e)
                else:
                    new_lambda_number += lambda_number.from_rainbow(e)
                for currentVertex in e.nodes:
                    if currentVertex != v:
                        boundaryVertexes.append(currentVertex)
            assert new_lambda_number
            new_iteration_values = copy.copy(self._iterationValues)
            if self._arrows_aware:
                arrow = graph_state.Arrow(graph_state.Arrow.NULL)
                propagator_arrow_diff_sign = 0
                if not edges[0].arrow.is_null():
                    if edges[1].arrow.is_null():
                        if boundaryVertexes[0] == edges[0].nodes[0]:
                            arrow = edges[0].arrow
                        else:
                            arrow = - edges[0].arrow
                    else:
                        adjusted_arrows = list()
                        for e in edges:
                            adjusted_arrows.append(e.arrow if v in e.nodes else (- e.arrow))
                        propagator_arrow_diff_sign = -1 if adjusted_arrows[0] == adjusted_arrows[1] else 1
                elif arrow.is_null() and not edges[1].arrow.is_null():
                    if boundaryVertexes[1] == edges[1].nodes[1]:
                        arrow = edges[1].arrow
                    else:
                        arrow = - edges[1].arrow
                if propagator_arrow_diff_sign:
                    new_lambda_number -= 1
                    new_iteration_values.append("(%s)" % propagator_arrow_diff_sign)
                newEdge = new_edge(boundaryVertexes,
                                   external_node=self._initGraph.externalVertex,
                                   colors=lambda_number.to_rainbow(new_lambda_number),
                                   arrow=arrow,
                                   marker=const.MARKER_1)
            else:
                newEdge = new_edge(boundaryVertexes,
                                   external_node=self._initGraph.externalVertex,
                                   colors=lambda_number.to_rainbow(new_lambda_number))
            newIterationGraphs = self._iterationGraphs + [self.getCurrentIterationGraph().change(edges, [newEdge])]
            newReducer = GGraphReducer(self._initGraph,
                                       useGraphCalculator=self._useGraphCalculator,
                                       rawFilters=True,
                                       subGraphFilters=self._subGraphFilter,
                                       iterationGraphs=newIterationGraphs,
                                       iterationValues=new_iteration_values)

            return newReducer.calculate()

    def _searchForChains(self):
        currentGraph = self.getCurrentIterationGraph()
        for v in currentGraph.vertices():
            if v is not currentGraph.externalVertex:
                edges = currentGraph.edges(v)
                if len(edges) == 2:
                    #checks no external edge
                    if currentGraph.externalVertex in edges[0].nodes or currentGraph.externalVertex in edges[1].nodes:
                        continue
                    return copy.copy(edges), v
        return None

    def getFinalValue(self):
        assert self.isSuccesfulDone()
        if str(self.getCurrentIterationGraph()).startswith("ee"):
            return "0", graph_state.Rainbow((0, 0))
        gValue = "*".join(map(lambda v: v if v[0] == 'G' else "(%s)" % v, self._iterationValues))
        innerEdge = None
        for e in self._iterationGraphs[-1].allEdges():
            if self._initGraph.externalVertex not in e.nodes:
                innerEdge = e
                break
        assert innerEdge

        wValue = innerEdge.colors

        if DEBUG:
            print "final", self._iterationGraphs
        return gValue, wValue

    def _putFinalValueToGraphStorage(self):
        storage.putGraph(self._initGraph, self.getFinalValue(), common.GFUN_METHOD_NAME_MARKER)