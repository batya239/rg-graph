#!/usr/bin/python
# -*- coding: utf8

import copy
import itertools

import nickel
import graph_state
import graphs
import nodes

import subgraphs
from dummy_model import _phi3_dyn

model = _phi3_dyn("phi3_dyn_test")

class DynGraph(graphs.Graph):
    def __init__(self, arg):
        self._lines = list()
        self._nodes = list()
        if isinstance(arg, str):
            self._from_graphstate(graph_state.GraphState.fromStr(arg))
        elif isinstance(arg, graph_state.GraphState):
            self._from_graphstate(arg)
        else:
            raise NotImplementedError, "Unsupported type of argument : %s" % arg


    def _from_graphstate(self, gs):
        edges = gs.sortings[0]
        _nodes = dict()
        line_idx = 0
        for line in edges:
            for node_idx in line.nodes:
                if not _nodes.has_key(node_idx):
                #                    _type=None if node_idx>=0 else -1

                #FIXME: all nodes are of the same type
                    _type = 1 if node_idx >= 0 else -1
                    _nodes[node_idx] = nodes.Node(type=_type)
            self._lines.append(_nodes[line.nodes[0]].AddLine(_nodes[line.nodes[1]], type=line.fields.pair))
            self._lines[-1]._idx = line_idx
            line_idx += 1

        self._nodes = DynGraph.indexed_nodes(_nodes)

    @staticmethod
    def indexed_nodes(nodes_dict):
        res = list()
        for node_idx in nodes_dict.keys():
            node = nodes_dict[node_idx]
            node._idx = node_idx
            res.append(node)
        return res


gs = graph_state.GraphState.fromStr("e12-23-3-e-:0AaAaa-aAaa-aA-0a:")
#gs = graph_state.GraphState.fromStr("e12-e3-45-45-5--:0AaAaA-0aaA-aAaa-aaaa-aA--:")
#gs = graph_state.GraphState.fromStr("e12-e3-33--:0AaAaA-0aaa-aAaa--:")

dG = DynGraph(gs)

dG.FindSubgraphs(model)
#subgraphs.RemoveTadpoles(dG)

def baseTRelations(graph):
    res = list()
    for line in graph._lines:
        if line.type == ('a', 'A'):
            res.append(tuple(map(lambda x: x.idx(), line.Nodes())))
        #        elif line.type == ('0','A'):
        #            res.append(line.Nodes())
        elif line.type == ('A', 'a'):
            res.append(tuple([x.idx() for x in reversed(line.Nodes())]))
    return res


def TRelations(graph):
    base = baseTRelations(graph)
    res = set(base)

    stop = False
    while not stop:
        tres = list()
        stop = True
        for trel1 in res:
            node = trel1[1]
            for trel2 in res:
                if trel2[0] == node and (trel1[0], trel2[1]) not in res:
                    tres.append((trel1[0], trel2[1]))
                    stop = False
        res = res | set(tres)
    res_ = dict()
    for node1, node2 in res:
        if not res_.has_key(node2):
            res_[node2] = list()
        res_[node2].append(node1)
    return res_


def TVersions(graph):
    trelations = TRelations(graph)
    nodes = [x.idx() for x in graph.xInternalNodes()]
    nnodes = len(nodes)
    res = list()
    for nodes_ in itertools.permutations(nodes):
        good = True
        for i in range(nnodes):
            node = nodes_[i]
            if trelations.has_key(node) and len(set(nodes_[i:]) & set(trelations[node])) <> 0:
                good = False
                break
        if good:
            res.append(nodes_)

    return res


def TCuts(graph, tversion):
    res = list()
    for i in range(len(tversion) - 1):
        tcut = list()
        left = set(tversion[:i + 1])
        right = set(tversion[i + 1:])
        for line in graph.xInternalLines():
            node1, node2 = map(lambda x: x.idx(), line.Nodes())
            if (node1 in left and node2 in right) or (node1 in right and node2 in left):
                tcut.append(line.idx())
        res.append(tcut)
    return res


def EffectiveSubgraphDim(subgraph, tCuts, model):
    sub = set([x.idx() for x in subgraph.lines])
    cnt = 0
    for tCut in tCuts:
        if len(sub & set(tCut)) <> 0:
            cnt += 1
    return subgraph.Dim(model) - model.freq_dim * (cnt - (len(subgraph.InternalNodes()) - 1) )

for tVersion in TVersions(dG):
    tCuts = TCuts(dG, tVersion)
    print
    print tVersion, tCuts
    for sub in dG._subgraphs:
        print sub.Dim(model), EffectiveSubgraphDim(sub, tCuts, model), sub

