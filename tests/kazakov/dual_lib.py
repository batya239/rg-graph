import copy
import time
import itertools
import sys
import graph_state

__author__ = 'mkompan'

from graph_state_builder_dual import gs_builder as gs_builder_dual
from graph_state_builder_loops import gs_builder, Rainbow
import graphine


def mark_border_edges(graph):
    new_edges = list()
    bound = graph.get_bound_vertices()
    for edge in graph.edges():
        if len(set(edge.nodes) & bound ) != 0:
            new_edge = gs_builder.new_edge(edge.nodes, colors=Rainbow(('e',)))
            new_edges.append(new_edge)
        else:
            new_edges.append(gs_builder.new_edge(edge.nodes, colors=Rainbow(tuple())))
    return graphine.Graph(new_edges)


def find_unused_edged(edges):
    res = list()
    for edge in edges:
        # print edge, edge.colors
        if len(edge.colors)<2 and not edge.is_external():
            res.append(edge)
    return res


def find_minimal_loop(graph, vertex):
    unused_edges = find_unused_edged(graph.edges(vertex))
    if len(unused_edges) < 2:
        return None
    else:
        loop_found = False

        branches = list()
        for edge in unused_edges:
            branch = ([edge], set(edge.nodes), list(set(edge.nodes)-set([vertex]))[0])
            branches.append(branch)

        loops = list()
        while not loop_found and len(branches)!=0:
            # print branches
            new_branches = list()
            for branch in branches:
                edges_list, vertices, tail = branch
                for edge in find_unused_edged(graph.edges(tail)):
                    if edge in edges_list:
                        continue
                    new_tail = list(set(edge.nodes)-set([tail]))[0]
                    if new_tail == vertex:
                        loop_found = True
                        loops.append(edges_list + [edge])
                    elif new_tail not in vertices:
                        new_branches.append((edges_list+[edge], vertices | set(edge.nodes), new_tail))
            branches = new_branches

    return loops if len(loops)>0 else None


def color_loops(graph, loop, mark):
    new_edges = list()
    for edge in graph.edges():
        if edge in loop:
            new_edge = gs_builder.new_edge(edge.nodes, colors=Rainbow(list(edge.colors)+[mark]))
            new_edges.append(new_edge)
        else:
            new_edges.append(edge)
        # print new_edges
    return graphine.Graph(new_edges)


def find_loops(graph):
    loop_cnt = 0
    g = graph
    for vertex in g.get_bound_vertices():
        # print find_unused_edged(g2.edges(vertex))

        loops = find_minimal_loop(g, vertex)
        # print vertex, loop_cnt, loops
        if loops is not None:
            g = color_loops(g, loops[0], loop_cnt)
            loop_cnt += 1
        # print g, loop_cnt
        # print
    for vertex in set(g.vertices)-g.get_bound_vertices()-set([g.external_vertex]):
        loops = find_minimal_loop(g, vertex)
        # print vertex, loop_cnt, loops
        if loops is not None:
            g = color_loops(g, loops[0], loop_cnt)
            loop_cnt += 1
    # print g
    if not (loop_cnt == graph.loops_count and
            reduce(lambda x, y:  x & y, map(lambda x: len(x.colors) > 0, g.internal_edges))):
        return None
    else:
        return g


def mark_external_edges(graph):
    ext_dual_vertices_cnt = 0
    edges_to_replace = dict()
    bound = graph.get_bound_vertices()
    visited = list()
    v = list(bound)[0]
    while v not in visited:
        edges = get_possible_external_path_edges(graph, v)
        if len(edges) == 0:
            continue
        current_vertex = v

        while current_vertex not in (bound-set([v])):
            edges = get_possible_external_path_edges(graph, current_vertex)
            for edge in edges:
                if edge not in edges_to_replace:
                    break
            # print edge, curent_vertex, edges_to_replace
            colors = list(edge.colors)
            try:
                colors.remove('e')
            except ValueError:
                pass
            colors = ['e%s'%ext_dual_vertices_cnt] + colors
            edges_to_replace[edge] = gs_builder.new_edge(edge.nodes, colors=Rainbow(colors))
            current_vertex = next_vertex(edge, current_vertex)
        ext_dual_vertices_cnt += 1
        visited.append(v)
        v = current_vertex
        # print edges_to_replace
    res = graph.change(edges_to_replace.keys(), edges_to_replace.values())
    return res


def get_possible_external_path_edges(graph, vertex):
    res = list()
    for edge in graph.edges(vertex):
        if not edge.is_external() and ('e' in edge.colors or len(edge.colors)==1):
            res.append(edge)
    return res


def next_vertex(edge, v):
    return list(set(edge.nodes)-set([v]))[0]


def graph_with_momenta(graph):
    return mark_external_edges(find_loops(mark_border_edges(graph)))


def dual_graph(graph_with_momenta_, mark_loops=True):
    dual_nodes = dict()
    node_cnt = 0
    new_edges = list()
    for edge in graph_with_momenta_.internal_edges:
        for color in edge.colors:
            if color not in dual_nodes:
                dual_nodes[color] = gs_builder_dual.new_node(node_cnt, n_num=color if mark_loops or isinstance(color, str) else 0)
                node_cnt += 1
        new_edges.append(gs_builder_dual.new_edge((dual_nodes[edge.colors[0]], dual_nodes[edge.colors[1]])))
    return graphine.Graph(gs_builder_dual.GraphState(new_edges))


def remove_loop_marks(dual_graph_):
    vertex_map=dict()
    for vertex in dual_graph_.vertices:
        vertex_map[vertex]=gs_builder_dual.new_node(dual_graph_.create_vertex_index(), n_num=vertex.n_num[2] if isinstance(vertex.n_num, str) else 0)
    new_edges = list()
    for edge in dual_graph_.edges():
        new_edges.append(gs_builder_dual.new_edge((vertex_map[edge.nodes[0]],vertex_map[edge.nodes[1]]), colors=edge.colors))
    # print new_edges
    return graphine.Graph(gs_builder_dual.GraphState(new_edges))


def check_pair(pair, dual):
    n1, n2 = pair
    # print pair
    # print len(dual.edges(n1, n2))
    # print len(set(map(lambda x: x.co_node(n1), dual.edges(n1))) & set(map(lambda x: x.co_node(n2), dual.edges(n2))))
    # print sorted([n1.n_num, n2.n_num]), sorted([n1.n_num, n2.n_num]) in [['e0', 'e2'], ['e1', 'e3']]
    if sorted([n1.n_num, n2.n_num]) in [['e0', 'e2'], ['e1', 'e3']]:
        res = True
    elif len(dual.edges(n1, n2))>0:
        res = False
    # elif len(set(map(lambda x: x.co_node(n1), dual.edges(n1))) & set(map(lambda x: x.co_node(n2), dual.edges(n2))))==0:
    #     res = False
    else:
        res = True
    # print res
    return res


def pairs2(items_dict, banned, dual):
    keys = items_dict.keys()
    if len(keys) == 0:
        yield []
    elif len(keys) < 2:
        return
        raise ValueError("items: %s" % items_dict)
    elif len(keys) == 2:
        if frozenset(keys) not in banned and check_pair(keys, dual):
            new_items_dict = copy.copy(items_dict)
            for key in keys:
                if new_items_dict[key] == 1:
                    del new_items_dict[key]
                else:
                    new_items_dict[key] -= 1
            for p in pairs2(new_items_dict, banned, dual):
                yield [tuple(keys)]+p
    else:
        for i in xrange(len(keys)):
            for j in xrange(i+1, len(keys)):
                pair = frozenset([keys[i], keys[j]])
                if pair not in banned and check_pair(pair,  dual):
                    new_items_dict = copy.copy(items_dict)
                    for key in pair:
                        if new_items_dict[key] == 1:
                            del new_items_dict[key]
                        else:
                            new_items_dict[key] -= 1

                    for k in pairs2(new_items_dict, banned, dual):
                        yield [tuple(pair)] + k


def get_pairs(nodes_to_connect, banned, dual):
    if sum(nodes_to_connect.values()) % 2 != 0:
        raise ValueError("items: %s" % nodes_to_connect)
    res = frozenset(tuple(sorted(x)) for x in pairs2(nodes_to_connect, banned, dual))
    return list(res)


def get_nodes_to_pair(graph):
    nodes_to_connect = dict()
    for node in graph.vertices:
        if isinstance(node.n_num, str):
            index = len(graph.edges(node))
        else:
            index = len(graph.edges(node))-4
        if index < 0:
            raise ValueError("negative index %s %s"% (node, graph))
        elif index != 0:
            nodes_to_connect[node] = index
    return nodes_to_connect


def dual_uv_index(graph):
    D = 6
    res = 0
    for node in graph.vertices:
        if node.n_num not in ('s','t'):
            res += D
    for edge in graph.edges():
        if edge.colors >= 1:
            res += 2*edge.colors
        elif edge.colors == 0:
            res -= 2
        else:
            raise NotImplementedError("%s" % edge)
    return res

def generate_pairings(dual):
    external_nodes_map = dict()
    for node in dual.vertices:
        if isinstance(node.n_num, str):
            external_nodes_map[node.n_num]=node

    banned = [frozenset(map(lambda x: external_nodes_map[x], ['e0', 'e1'])),
              frozenset(map(lambda x: external_nodes_map[x], ['e0', 'e3'])),
              frozenset(map(lambda x: external_nodes_map[x], ['e1', 'e2'])),
              frozenset(map(lambda x: external_nodes_map[x], ['e2', 'e3'])),
              ]
    for edge in dual.edges():
        banned.append(frozenset(edge.nodes))


    nodes_to_connect = get_nodes_to_pair(dual)


    pairs = get_pairs(nodes_to_connect, banned, dual)
    return pairs

def extract_st(n_num):
    if isinstance(n_num, str):
        return n_num[2]
    else:
        return None