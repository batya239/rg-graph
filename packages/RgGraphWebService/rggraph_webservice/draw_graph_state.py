#!/usr/bin/python

import nickel
import pydot


def generate_png_stream(nomenkl):
    nomenkl = nomenkl.replace("-", "|")
    edges = nickel.Nickel(string=nomenkl).edges
    nickel_ = str(nickel.Canonicalize(edges))
    g = pydot.Dot(graph_type="graph")
    g.add_subgraph(_cluster(nickel_))
    return g.create_png()


def _prepare(nomenkl):
    def is_internal(_node):
        return _node != -1

    edges = nickel.Nickel(string=nomenkl).edges

    lines = []
    nodes = dict()
    ext_cnt = 0
    for edge in edges:
        nodes__ = list()
        for node in edge:
            if is_internal(node):
                nodes__.append(("%s_%s" % (nomenkl, node), "%s" % node))
            else:
                nodes__.append(("%s_E_%s" % (nomenkl, ext_cnt), "ext"))
                ext_cnt += 1
            if nodes__[-1][0] not in nodes.keys():
                nodes[nodes__[-1][0]] = nodes__[-1][1]
        lines.append([n[0] for n in nodes__])
    return nodes, lines


def _cluster(nomenkl):
    font_size = "12"
    width = "0.1"
    nodes, lines = _prepare(nomenkl)
    cluster = pydot.Cluster(nomenkl.replace('|', '_'), label=nomenkl)
    for node in nodes:
        if nodes[node] == 'ext':
            cluster.add_node(pydot.Node(node, label='""', fontsize=font_size, width=width, color='white'))
        else:
            cluster.add_node(pydot.Node(node, label='"%s"' % nodes[node], fontsize=font_size, width=width))

    for line in lines:
        cluster.add_edge(pydot.Edge(line[0], line[1]))
    return cluster