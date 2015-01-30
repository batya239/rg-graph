#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

import graph_state as gs
import networkx as nx
import itertools as it
import matplotlib.pyplot as plt
import dynamic_diagram_generator

def draw_nx_graph(G,spines,nom):
    """
    Buggy in case of MultiGraph()
    """
    #plt.xkcd() ## WOW!!!!
    n = len(spines)
    region = 230
    pos = None
    for i in range(n):
        region += 1
        plt.subplot(region)
        plt.title("number %d"%(i))
        new_G = nx.MultiGraph()
        new_G.add_path(spines[i][0],color = 'blue', weight = 2)
        new_G.add_path(spines[i][1],color = 'red',  weight = 2)
        rest_edges = [e for e in G.edges() if e not in new_G.edges()]
        new_G.add_edges_from(rest_edges,color = 'black',weight=1)
        edges = new_G.edges()
        colors = [new_G[u][v][0]['color'] for u,v in edges]
        weights = [new_G[u][v][0]['weight'] for u,v in edges]
        if not pos:
            pos=nx.spring_layout(new_G)
        nx.draw(new_G,pos,node_size=1, edge_color=colors, width=weights)
    #plt.show()
    plt.savefig('%s.png'%nom)
    plt.close('all')

def draw_Agraph(G,spines,nom):
    n = len(spines)
    for i in range(n):
        new_G = nx.MultiGraph()
        new_G.add_path(spines[i][0],color = 'blue', weight = 2)
        new_G.add_path(spines[i][1],color = 'red',  weight = 2)
        rest_edges = [e for e in G.edges() if e not in new_G.edges()]
        new_G.add_edges_from(rest_edges,color = 'black',weight=1,dir = 'forward', arrowhead = 'dot')
        a = nx.to_agraph(new_G)
        a.layout(prog='circo')
        #a.node_attr.update(shape="circle")
        a.draw('%s_%d.png'%(nom,i))

def draw_Agraph_with_fields(nickel_str):
    if not isinstance(nickel_str,str):
        nickel_str = str(nickel_str)
    G = nx_graph_from_str(nickel_str)
    new_G = nx.MultiDiGraph()
    lines = {'d':'dot', 'a':'none','A':'tee','0':'none'}

    for e in set(G.edges()):
        i,j = e
        for r in range(len(G[i][j])):
            # print lines[G[i][j][r]['fields'][0]]
            new_G.add_edge(*e,arrowtail = lines[G[i][j][r]['fields'][0]],arrowhead = lines[G[i][j][r]['fields'][1]],dir='both')
    a = nx.to_agraph(new_G)
    a.layout(prog='circo')
    # nx.draw(new_G)
    # plt.show()
    a.draw('%s.png'%(nickel_str))

def nx_graph_from_str(nickel_str):
    """
    Returns networkx MultiGraph object from Nickel string
    NB: here we 'forget' about graph_state ancestry
    """
    if not ":" in str(nickel_str):
        gs_diag = static_diag(nickel_str)
        edges = [tuple(map(lambda n: n.index, e.nodes)) for e in gs_diag.edges]
        ext = [e for e in edges if -1 in e]
        ext_index = lambda x: 1-x.index(-1)
        g = nx.MultiGraph()

        for i,e in enumerate(ext):
                edges.remove(e)
                edges.append((e[ext_index(e)],-i-1))
        g.add_edges_from(edges)

    else:
        gs_diag = dynamic_diag(nickel_str)
        edges = [e for e  in gs_diag.edges if not e.is_external()]
        # ext = [tuple(map(lambda n: n.index, e.nodes)) for e  in gs_diag.edges if e.is_external()]
        ext = [e for e  in gs_diag.edges if e.is_external()]

        g = nx.MultiDiGraph()
        for e in edges:
            i,j = tuple(map(lambda n: n.index, e.nodes))
            g.add_edge(i,j,fields = e.fields)
        for k,e in enumerate(ext):
            i,j = tuple(map(lambda n: n.index, e.nodes))
            g.add_edge(-k-1,j,fields = e.fields)
    #nx.write_dot(g,'multi.dot')
    return g

def static_diag(diag_from_str):
    sc = gs.PropertiesConfig.create()
    return sc.graph_state_from_str(diag_from_str)

def dynamic_diag(diag_from_str):
    sc = gs.PropertiesConfig.create(
                gs.PropertyKey(name="fields",
                                is_directed=True,
                                externalizer=gs.Fields.externalizer()))
    return sc.graph_state_from_str(diag_from_str)


def spine(G,source,sink):
    """
    Returns spine pairs array for certain pair (source,sink)
        in networkx graph G
    """
    spine_pairs = []
    all_paths = [p for p in nx.all_simple_paths(G,source,sink)]
    for s in it.combinations(all_paths,2):
        if set(s[0][1:-1]).intersection(set(s[1][1:-1])) == set():
            spine_pairs.append(s)
    return spine_pairs

def filter_spines(G,spines):
    """
    @param G:
    @param spines:
    @return: True if graph G has spine from 'spines'
    """

    all_vertices = G.vertices
    vertices = sorted(all_vertices)
    vertices.remove(G.external_vertex)

    # print "All vertices:",vertices
    # print [v for v in G.edges(vertices[0]) if not v.is_external()]

    source = vertices[0]
    # print "Source:",source
    ## Search for spine candidate
    q = [source]
    visited_vertices = []#set()
    while q:
        v = q.pop()
        # print "v =",v
        if v in visited_vertices:
            continue
        visited_vertices += [v]
        for e in [k for k in G.edges(v)]:
            # print "try",e
            next_node = e.co_node(v)
            if str(e.fields) == 'aA' and next_node not in visited_vertices:
                # print "Next edge:",next_node
                q = [next_node] + q
                break
    print "Spine:",visited_vertices
    half_spine_candidates = []
    for sp in spine_pairs:
        if visited_vertices in sp:
            # print "Spine found:",sp[1-sp.index(visited)], "%d times"%sp.count(visited)
            half_spine_candidates += [sp[1-sp.index(visited_vertices)]]
    half_spine_candidates = set(tuple(row) for row in half_spine_candidates)

    # print "Visited:",visited_vertices, map(lambda x: list(visited_vertices) in x, spine_pairs)

    if half_spine_candidates:
        print "Half-spine candidates:", half_spine_candidates
    else:
        print "\tFiltered: no half-spine candidate"
        return None
    for sc in half_spine_candidates:
        print "current candidate:", sc
        sink = sc[-1]
        if len(G.edges(source,sink)) > 0:
            for e in G.edges(source,sink):
                if str(e.fields) == 'dd':
                    return True
        # print "First edge of hs:",G.edges(*sc[:2])
        # print "Last edge of hs:",G.edges(*sc[-2:])

        if str(G.edges(*sc[0:2])[0].fields) not in ['da','dA']:
            return None
        elif str(G.edges(*sc[-2:])[0].fields) not in ['ad','Ad']:
            return None
        # for v in sc:
        #     print "\t\t",v

    """
    ## Search for half-spine candidate
    q = [source]
    visited_vertices = []

    ## First edge
    # print "Source:", source, " sink:",sink
    for e in [k for k in G.edges(source)]:
        # print "try",e
        next_node = e.co_node(source)
        if str(e.fields) == 'dd':
            # print "dd, next_node =",next_node
            if next_node == sink:
                return [source,sink]
            else:
                return None
        elif (str(e.fields) == 'dA' or str(e.fields) == 'da') \
                and next_node not in visited_vertices:
            # print "Next edge:",next_node
            q = [next_node] + q
            visited_vertices += [next_node]
    # print "\tHalf spine:",visited_vertices
    ## Half-spine
    while q:
        v = q.pop()
        # print "v =",v
        if v in visited_vertices:
            continue
        visited_vertices += [v]
        for e in [k for k in G.edges(v)]:
            # print "try",e
            next_node = e.co_node(v)
            if (str(e.fields) == 'aA' or str(e.fields) == 'aa') \
                    and next_node not in visited_vertices: #\
                    # and next_node not in full_spine:
                # print "Next edge:",next_node
                q = [next_node] + q
                break

    ## Last edge
    for e in [k for k in G.edges(sink)]:
        prew_node = e.co_node(sink)
        if prew_node == visited_vertices[-1]:
            # print "prew edge:",prew_node, "sink:",sink
            if str(e.fields) == 'ad' or str(e.fields) == 'Ad':
                # print "not dd"
                return visited_vertices + [next_node]
            else:
                # print "xxx"
                return None
        # elif (str(e.fields) == 'dA' or str(e.fields) == 'da') \
        #         and next_node not in visited_vertices:
            # print "Next edge:",next_node
            # q = [next_node] + q
    print "half spine:",visited_vertices
    """
    return True


if  __name__ == "__main__":
    with open("../e2-2loop.txt.gs") as fd:
        diags = [d.strip() for d in fd.readlines()]
    count_all, count_good = 0,0
    for d in diags[:1]:
        print "\n",d
        G = nx_graph_from_str(d)
        source = 0
        sink = max([g for g in G.edges() if g[1] < 0])[0]
        spine_pairs = spine(G,source,sink)
        # draw_Agraph(G,spine_pairs,d.replace('|','-'))
        print "Spine pairs",spine_pairs
        for _g in dynamic_diagram_generator.generate(d, possible_fields=["aA", "aa", "ad", "dd", "dA"], possible_external_fields="Aa", possible_vertices=["adA"]):
            print "_"*5
            count_all +=1
            if filter_spines(_g,spine_pairs):
                count_good +=1
                print _g
                draw_Agraph_with_fields(_g)
    print "All: %d, good: %d"%(count_all,count_good)