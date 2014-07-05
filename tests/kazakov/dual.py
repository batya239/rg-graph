import copy
import time
import itertools
import sys

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
    if not (loop_cnt != graph.loops_count and
            reduce(lambda x, y:  x & y, map(lambda x: len(x.colors) == 2, g.internal_edges))):
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




def dual_graph(graph):
    g = mark_external_edges(find_loops(mark_border_edges(graph)))
    dual_nodes = dict()
    node_cnt = 0
    new_edges = list()
    for edge in g.internal_edges:
        for color in edge.colors:
            if color not in dual_nodes:
                dual_nodes[color] = gs_builder_dual.new_node(node_cnt, n_num=color if isinstance(color, str) else 0)
                node_cnt += 1
        new_edges.append(gs_builder_dual.new_edge((dual_nodes[edge.colors[0]], dual_nodes[edge.colors[1]])))
    return graphine.Graph(gs_builder_dual.GraphState(new_edges))



def pairs2(items_dict, banned):
    keys = items_dict.keys()
    if len(keys) == 0:
        yield []
    elif len(keys) < 2:
        return
        raise ValueError("items: %s" % items_dict)
    elif len(keys) == 2:
        if frozenset(keys) not in banned:
            new_items_dict = copy.copy(items_dict)
            for key in keys:
                if new_items_dict[key] == 1:
                    del new_items_dict[key]
                else:
                    new_items_dict[key] -= 1
            for p in pairs2(new_items_dict, banned):
                yield [tuple(keys)]+p
    else:
        for i in xrange(len(keys)):
            for j in xrange(i+1, len(keys)):
                pair = frozenset([keys[i], keys[j]])
                if pair not in banned:
                    new_items_dict = copy.copy(items_dict)
                    for key in pair:
                        if new_items_dict[key] == 1:
                            del new_items_dict[key]
                        else:
                            new_items_dict[key] -= 1

                    for k in pairs2(new_items_dict, banned):
                        yield [tuple(pair)] + k


def get_pairs(nodes_to_connect, banned):
    if sum(nodes_to_connect.values()) % 2 != 0:
        raise ValueError("items: %s" % nodes_to_connect)
    res = frozenset(tuple(sorted(x)) for x in pairs2(nodes_to_connect, banned))
    if len(res) >1:
        raise Exception("not unique pairing %s" % res)
    return list(res)



# gs = gs_builder.graph_state_from_str("e12|e3|34|5|e5|e|:")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|e7|e|:")
# gs = gs_builder.graph_state_from_str("e12|e3|34|5|56|7|89|8A|B|eB|eB||:")
gs = gs_builder.graph_state_from_str("e12|23|4|e5|67|89|7A|B|eC|eC|BD|D|D||:")

# gs = gs_builder.graph_state_from_str("%s:"%sys.argv[1])
print gs

g = graphine.Graph(gs)



start = time.time()
try:
    g5 = dual_graph(g)
except:
    print "Failed to construct dual graph"
    sys.exit(1)
finally:
    print time.time()-start


external_nodes_map = dict()
for node in g5.vertices:
    if isinstance(node.n_num, str):
        external_nodes_map[node.n_num]=node

banned = [frozenset(map(lambda x: external_nodes_map[x], ['e0', 'e1'])),
          frozenset(map(lambda x: external_nodes_map[x], ['e0', 'e3'])),
          frozenset(map(lambda x: external_nodes_map[x], ['e1', 'e2'])),
          frozenset(map(lambda x: external_nodes_map[x], ['e2', 'e3'])),
          ]
for edge in g5.edges():
    banned.append(frozenset(edge.nodes))

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

try:
    nodes_to_connect = get_nodes_to_pair(g5)
except ValueError, e:
    print "negative index in vertex %s\n %s" % (g5, e)
    sys.exit(1)

# print nodes_to_connect
# print banned

start = time.time()
try:
    pairs = get_pairs(nodes_to_connect, banned)
except Exception,e:
    print g, g5, e
    sys.exit(1)
if len(pairs) == 0:
    print "no pairings"
    sys.exit(1)
print g, "dual:", g5
print "pairs", pairs
print time.time()-start
print

