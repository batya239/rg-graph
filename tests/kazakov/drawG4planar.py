#!/usr/bin/python
# -*- coding: utf8
import time
import sys
import numpy

__author__ = 'mkompan'

from graph_state_builder_loops import gs_builder as gs_builder_loops
from graph_state_builder_dual import gs_builder as gs_builder_dual

import vertex
import graphine
from matplotlib import pyplot as plt

from collections import namedtuple

edge_poly = namedtuple('edge_poly', ['poly', 'swaped', 'start', 'end'])

def find_ext_momentum_coloured_g4(graph):
    ext_momentum = dict()
    for i in range(4):
        en = 'e%s' % i
        edge_list = list()
        for edge in graph.internal_edges:
            if en in edge.colors:
                edge_list.append(edge)
        vertex_list = list(edge_list[0].nodes)
        edge_list = edge_list[1:]
        while len(edge_list)>0:
            v1, v2 = vertex_list[0], vertex_list[-1]
            for edge in edge_list:
                if v1 in edge.nodes:
                    edge_list.remove(edge)
                    vertex_list = [edge.co_node(v1)]+vertex_list
                elif v2 in edge.nodes:
                    edge_list.remove(edge)
                    vertex_list.append(edge.co_node(v2))
        ext_momentum[en] = vertex_list
    return ext_momentum

def generate_vertex_map(g, ext_momentum_map, fixed_vertices):
    corners = [('e0', 'e1'), ('e1', 'e2'), ('e2', 'e3'), ('e3', 'e0')]
    corners_map = {'e0': (0, 3), 'e1': (0, 1), 'e2': (1, 2), 'e3': (2, 3)}

    def get_corner_number(node, ext_momentum_map):
        for i in range(4):
            if node in ext_momentum_map[corners[i][0]] and node in ext_momentum_map[corners[i][1]]:
                return i
        raise ValueError("vertex %s is not bound vertex" % node)

    all_fixed = reduce(lambda x,y: x|y, map(set,ext_momentum_map.values()))
    # print all_fixed
    vertices_map = dict()
    for node in g.vertices:
        # print node, ext_momentum_map, fixed_vertices
        if node == g.external_vertex:
            continue
        elif node in fixed_vertices:
            corner = get_corner_number(node, ext_momentum_map)
            v = vertex.Vertex(_FIXED_POS_G4_1[corner], q=0.0, fixed=True, r=vertex.VERTEX_SIZE)
            # print "corner", corner, v, node
        elif node in all_fixed:
            for en in corners_map:
                if node not in ext_momentum_map[en]:
                    continue
                c1, c2 = corners_map[en]
                # print en, node, ext_momentum_map[en]
                idx = ext_momentum_map[en].index(node) \
                    if get_corner_number(ext_momentum_map[en][0], ext_momentum_map) == c1 \
                    else len(ext_momentum_map[en])-1-ext_momentum_map[en].index(node)
                pos = _FIXED_POS_G4_1[c1]+idx*(_FIXED_POS_G4_1[c2]-_FIXED_POS_G4_1[c1])/(len(ext_momentum_map[en])-1)
                v = vertex.Vertex(pos, fixed=True, r=vertex.VERTEX_SIZE)
                # print v, idx
                break
        else:
            v = vertex.Vertex(_NONFIXED_POS_G4, r=vertex.VERTEX_SIZE)

        vertices_map[node] = v
    return vertices_map

def arrange_vertices(g, V, vertices_map, n=500):
    for edge in g.internal_edges:
        v1, v2 = map(lambda x: vertices_map[x], edge.nodes)
        vertex.Vertex.link(v1, v2)

    vertex.random_shift(V)
    vertex.constant_shift(V)
    vertex.K = 0.1
    start = time.time()
    vertex.evaluate_vertices(V, n=n)
    print time.time() - start

    for v in V:
        v.fix()
        v.q = 0.01
        v.neighbours = list()

    vertex.K = 0.01

def get_edge_map(edges, vertices_map):
    edge_map = dict()
    for edge in edges:
        v1, v2 = map(lambda x: vertices_map[x], edge.nodes)
        # print edge, edge.edge_id, v1, v2
        edge_nodes = [v1, ]
        while edge_nodes[-1] != v2:
            v = edge_nodes[-1]
            # print "v", v
            for n in v.neighbours:
                # print "n",n
                if (n not in edge_nodes and n.get_property('edge_id') == edge.edge_id) or n == v2:
                    edge_nodes.append(n)
                    break
        #edge_list.append(zip(*map(lambda x: x.pos, edge_nodes)))
        edge_map[edge]=edge_nodes
    return edge_map

def is_ordered(lst):
    direction = lst[0] > lst[-1]
    return reduce(lambda x, y: x & y, [(lst[i] > lst[i + 1]) == direction for i in range(len(lst) - 1)])


def get_edge_pos_map(edges_to_evaluate, vertices_map):
    edge_map = get_edge_map(edges_to_evaluate, vertices_map)
    edge_pos_map = dict()
    for edge in edge_map:
        edge_nodes = edge_map[edge]
        edge_pos_map[edge]=zip(*map(lambda x: x.pos, edge_nodes))
    return edge_pos_map


def fit_edges(edges_to_evaluate, vertices_map, edges=None):
    edge_pos_map = get_edge_pos_map(edges_to_evaluate, vertices_map)
    edge_polys_map = dict()
    for edge in edge_pos_map:
        x,y = edge_pos_map[edge]
        if abs(x[0]-x[-1]) > abs(y[0]-y[-1]):
            if is_ordered(x):
                swap = False
                x_, y_ = x, y
            elif is_ordered(y):
                swap = True
                x_, y_ = y, x
            else:
                print x
                print y

                raise NotImplementedError("sss1 %s %s" % (is_ordered(x),is_ordered(y) ))
        else:
            if is_ordered(y):
                swap = True
                x_, y_ = y, x
            elif is_ordered(x):
                swap = False
                x_, y_ = x, y
            else:
                print x
                print y
                raise NotImplementedError("sss2 %s %s" % (is_ordered(x),is_ordered(y) ))
        w = numpy.zeros_like(x_) + 0.1
        w[0] = 1.
        w[-1] = 1.
#            poly = numpy.poly1d(numpy.polyfit(x_, y_, len(x_) - 2, w=w))
        poly = numpy.poly1d(numpy.polyfit(x_, y_, 2, w=w))
        edge_polys_map[edge]=edge_poly(poly, swap, x_[0], x_[-1])
    return edge_polys_map

def draw_planar_g4(coloured_graph):
    fixed_vertices = coloured_graph.get_bound_vertices()
    if len(fixed_vertices) != 4:
        raise NotImplementedError('fixed: %s' % fixed_vertices)



    ext_momentum_map = find_ext_momentum_coloured_g4(coloured_graph)


    vertices_map = generate_vertex_map(coloured_graph, ext_momentum_map, fixed_vertices)
    V = vertices_map.values()

    arrange_vertices(coloured_graph, V, vertices_map, n=50)

    cnt = _FIGURE_INDEX.next()
    fig = plt.figure(cnt+1)

    for v in V:
        # print v
        if v.get_property('edge_id') is None:
            plt.scatter(v.pos[0], v.pos[1], s=v.get_property('r'))
    for edge in coloured_graph.internal_edges:
        n1,n2 = map(lambda x: vertices_map[x], edge.nodes)
        x,y = zip(n1.pos, n2.pos)
        plt.plot(x,y,'b')

    for i in range(4):
        x,y = zip(_FIXED_POS_G4_1[i], _FIXED_POS_G4_2[i])
        plt.plot(x,y,'b')
    string = str(coloured_graph.to_graph_state().topology_str())
    plt.title(string)
    plt.savefig("%s_%s.png" % (string, cnt), format='png')

def draw_planar_g4_dual(coloured_graph, coloured_dual, caption=None, filename=None, index=None):
    fixed_vertices = coloured_graph.get_bound_vertices()
    if len(fixed_vertices) != 4:
        raise NotImplementedError('fixed: %s' % fixed_vertices)

    ext_momentum_map = find_ext_momentum_coloured_g4(coloured_graph)


    vertices_map = generate_vertex_map(coloured_graph, ext_momentum_map, fixed_vertices)
    V = vertices_map.values()

    arrange_vertices(coloured_graph, V, vertices_map, n=100)
    if index is None:
        cnt = _FIGURE_INDEX.next()
    else:
        cnt = index
    fig = plt.figure(cnt+1)
    # fig = plt.figure(1)

    for v in V:
        # print v
        if v.get_property('edge_id') is None:
            plt.scatter(v.pos[0], v.pos[1], s=v.get_property('r'))
    for edge in coloured_graph.internal_edges:
        n1,n2 = map(lambda x: vertices_map[x], edge.nodes)
        x,y = zip(n1.pos, n2.pos)
        plt.plot(x, y, 'b')

    for i in range(4):
        x,y = zip(_FIXED_POS_G4_1[i], _FIXED_POS_G4_2[i])
        plt.plot(x, y, 'b')

    dual_vertices_map = dict()
    for node in coloured_dual.vertices:
        pos, color = dual_node_pos_and_color(node, coloured_graph, vertices_map)

        dual_vertices_map[node] = vertex.Vertex(pos, fixed=True, r=vertex.VERTEX_SIZE)
        plt.scatter(pos[0], pos[1], s=vertex.VERTEX_SIZE, c=color)

    edges_to_evaluate = list()
    for edge in coloured_dual.internal_edges:
        v1, v2 = map(lambda x: dual_vertices_map[x], edge.nodes)
        type_ = edge.colors if isinstance(edge.colors, int) else edge.colors[0]
        if type_==0:
            x,y = zip(v1.pos, v2.pos)
            plt.plot(x, y, _ST_COLORS['line%s' % type_])
        else:
            V = V + vertex.constant_shift(vertex.create_edge(v1, v2, n=3, edge_id=edge.edge_id))
            edges_to_evaluate.append(edge)
    start = time.time()
    vertex.evaluate_vertices(V, n=50)
    print time.time() - start

    edge_polys_map = fit_edges(edges_to_evaluate, dual_vertices_map)
    for edge in edge_polys_map:
        edge_poly_ = edge_polys_map[edge]
        step = (edge_poly_.end - edge_poly_.start) / _CURVE_POINTS
        x = numpy.arange(edge_poly_.start, edge_poly_.end + step, step)
        type_ = edge.colors if isinstance(edge.colors, int) else edge.colors[0]
        if not edge_poly_.swaped:
            plt.plot(x, edge_poly_.poly(x), _ST_COLORS['line%s' % type_], linewidth=2)
        else:
            plt.plot(edge_poly_.poly(x), x, _ST_COLORS['line%s' % type_], linewidth=2)
    if caption is None:
        caption = str(coloured_graph.to_graph_state().topology_str())

    plt.title(caption)
    if filename is None:
        filename = str(coloured_graph.to_graph_state().topology_str())
    plt.savefig("%s#%s.png" % (filename, cnt), format='png')


def dual_node_pos_and_color(node, coloured_graph, vertices_map):
    if isinstance(node.n_num, str):
        color = _ST_COLORS[node.n_num[2]]
        en = int(node.n_num[1])
        pos = _FIXED_POS_G4_DUAL[en]
        return pos, color
    else:
        pos = numpy.array([0.,0.])
        vertices = set()
        for edge in coloured_graph.internal_edges:
            if node.n_num in edge.colors:
                vertices = vertices | set(edge.nodes)
        for node in vertices:
            pos += vertices_map[node].pos
        return pos/len(vertices), _ST_COLORS[None]

_FIGURE_INDEX = vertex.xindex()
_EPS = 10**-6
_FIXED_POS_G4_1 = map(numpy.array, [(0., -5.), (0., 5.), (10., 5.), (10., -5.)])
_FIXED_POS_G4_2 = map(numpy.array, [(-0.8, -5), (-0.8, 5), (10.8, 5), (10.8, -5)])

_FIXED_POS_G4_DUAL = map(numpy.array, [(5., -7.), (-2., 0.), (5., 7.), (12, 0.) ])
_ST_COLORS = {'s': 'g', 't': 'c', None: 'r', 'line0': 'r-', 'line1': 'r--', 'line2': 'c--', 'line3': 'm--', 'line4': 'y--', 'line5': 'k--'}

_NONFIXED_POS_G4 = (5, 0)
_NONFIXED_POS_DUAL = (5, 0)
_CURVE_POINTS = 100


if __name__ == "__main__":
    input=["e12|e3|45|46|7|78|79||e9|e|:('e',)_('e0', 0)_('e1', 0)|('e',)_('e3', 0)|(0, 3)_('e1', 3)|(0, 2)_('e3', 2)|(2, 3)|(1, 3)_('e1', 1)|(1, 2)_('e3', 1)||('e',)_('e2', 1)|('e',)|",
           "12|34567|34567||5|6|7||:0_1|1_0_0_0_0|0_0_0_0_0||0|0|0||:e0t_0_1_e2t_e1s_3_2_e3s"]

    input = ["e12|e3|45|67|e8|89|eA|9A|B|B|B||:('e',)_('e0', 0)_('e1', 0)|('e',)_('e3', 0)|('e1', 2)_(0, 2)|('e3', 1)_(0, 1)|('e',)_('e2', 2)|(2, 4)_(0, 4)|('e',)_('e2', 1)|(0, 3)_(1, 3)|('e2', 4)|(3, 4)|('e2', 3)||",
             "1|222345678|3456|45|6|7|8|||:0|1_1_1_0_0_0_0_0_0|0_0_0_0|0_0|0|0|0|||:e0s_0_e2s_3_4_1_2_e3t_e1t"]
    # g = graphine.Graph(gs_builder.graph_state_from_str(sys.argv[1]))
    # g = graphine.Graph(gs_builder.graph_state_from_str("e12|e3|45|46|7|78|79||e9|e|:('e',)_('e0', 0)_('e1', 0)|('e',)_('e3', 0)|(0, 3)_('e1', 3)|(0, 2)_('e3', 2)|(2, 3)|(1, 3)_('e1', 1)|(1, 2)_('e3', 1)||('e',)_('e2', 1)|('e',)|"))
    # g = graphine.Graph(gs_builder.graph_state_from_str("e12|e3|34|5|56|7|89|8A|B|eC|BD|C|D|e|:('e',)_('e0', 0)_('e3', 0)|('e',)_('e1', 0)|(0, 3)_('e3', 3)|('e1', 3)|(3, 4)_('e3', 4)|('e1', 4)|(2, 4)_('e3', 2)|(4, 5)_('e1', 5)|(2, 5)|('e',)_('e2', 2)|(1, 5)_('e1', 1)|(1, 2)|('e2', 1)|('e',)|"))
    g = graphine.Graph(gs_builder_loops.graph_state_from_str(input[0]))
    dual = graphine.Graph(gs_builder_dual.graph_state_from_str(input[1]))

    # draw_planar_g4(g)
    draw_planar_g4_dual(g, dual, caption="$1^2$")
    plt.show()

    sys.exit()
