#!/usr/bin/python
# -*- coding: utf8

import nickel
import graph_state
import graphs
import nodes

import subgraphs
from dummy_model import _phi3_dyn
model=_phi3_dyn("phi3_dyn_test")

class DynGraph(graphs.Graph):
    def __init__(self, arg):
        self._lines = list()
        self._nodes = list()
        if isinstance(arg, str):
            self._from_graphstate(graph_state.GraphState.fromStr(arg))
        elif isinstance(arg, graph_state.GraphState):
            self._from_graphstate(arg)
        else:
            raise NotImplementedError, "Unsupported type of argument : %s"%arg


    def _from_graphstate(self, gs):
        edges = gs.sortings[0]
        _nodes=dict()
        line_idx=0
        for line in edges:
            for node_idx in line.nodes:
                if not _nodes.has_key(node_idx):
#                    _type=None if node_idx>=0 else -1

#FIXME: all nodes are of the same type
                    _type=1 if node_idx>=0 else -1
                    _nodes[node_idx]=nodes.Node(type=_type)
            self._lines.append(_nodes[line.nodes[0]].AddLine(_nodes[line.nodes[1]], type = line.fields.pair))
            self._lines[-1]._idx = line_idx
            line_idx+=1

        self._nodes=DynGraph.indexed_nodes(_nodes)

    @staticmethod
    def indexed_nodes(nodes_dict):
        res=list()
        for node_idx in nodes_dict.keys():
            node=nodes_dict[node_idx]
            node._idx=node_idx
            res.append(node)
        return node


gs = graph_state.GraphState.fromStr("e12-23-3-e-:0AaAaa-aAaa-aA-0a:")
gs = graph_state.GraphState.fromStr("e12-e3-45-45-5--:0AaAaA-0aaA-aAaa-aaaa-aA--:")
#gs=graph_state.GraphState.fromStr("e12-23-3-e-::")

dG=DynGraph(gs)
print dG

dG.FindSubgraphs(model)
#subgraphs.RemoveTadpoles(dG)

print
for sub in dG._subgraphs:
    print sub.Dim(model), sub
