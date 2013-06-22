#!/usr/bin/python

import nickel
import pydot


def generatePngStream(nomenkl):
    edges = nickel.Nickel(string=nomenkl).edges
    nickel_ = str(nickel.Canonicalize(edges))

    G = pydot.Dot(graph_type="graph")
    G.add_subgraph(_Cluster(nickel_))
    return G.create_png()


def _prepare(nomenkl):
    def isInternal(node):
        return node <> -1

    edges = nickel.Nickel(string=nomenkl).edges

    lines = []
    nodes = dict()
    ext_cnt = 0
    for edge in edges:
        nodes__ = list()
        for node in edge:
            if isInternal(node):
                nodes__.append(("%s_%s" % (nomenkl, node), "%s" % node))
            else:
                nodes__.append(("%s_E_%s" % (nomenkl, ext_cnt), "ext"))
                ext_cnt += 1
            if nodes__[-1][0] not in nodes.keys():
                nodes[nodes__[-1][0]] = nodes__[-1][1]
        lines.append([n[0] for n in nodes__])
    return nodes, lines


def _Cluster(nomenkl):
    fontsize = "12"
    width = "0.1"
    nodes, lines = _prepare(nomenkl)
    cluster = pydot.Cluster(nomenkl.replace('-', '_'), label=nomenkl)
    for node in nodes:
        if nodes[node] == 'ext':
            cluster.add_node(pydot.Node(node, label='""', fontsize=fontsize, width=width, color='white'))
        else:
            cluster.add_node(pydot.Node(node, label='"%s"' % nodes[node], fontsize=fontsize, width=width))

    for line in lines:
        cluster.add_edge(pydot.Edge(line[0], line[1]))
    return cluster
