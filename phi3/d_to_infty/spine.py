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
    lines = {'d':'dot', 'a':'none','A':'tee'}

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
        ext = [tuple(map(lambda n: n.index, e.nodes)) for e  in gs_diag.edges if e.is_external()]

        g = nx.MultiDiGraph()
        for e in edges:
            i,j = tuple(map(lambda n: n.index, e.nodes))
            g.add_edge(i,j,fields = e.fields)
        # for e in ext:
        print ext
        g.add_edge(-1,0,fields = 'aA')
        g.add_edge(ext[1][1],-2,fields = 'aa')
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

if  __name__ == "__main__":
    with open("../e2-3loop.txt.gs") as fd:
        diags = [d.strip() for d in fd.readlines()]
    for d in diags[:1]:
        print "\n",d
        G = nx_graph_from_str(d)
        source = 0
        # sink = max([g for g in G.edges() if type(g[1]) == str])[0]
        sink = max([g for g in G.edges() if g[1] < 0])[0]
        spine_pairs = spine(G,source,sink)
        #print "Spine pairs:",spine_pairs
        #draw_nx_graph(G,spine_pairs,d.replace('|','-'))
        draw_Agraph(G,spine_pairs,d.replace('|','-'))
        print "Spine pairs",spine_pairs
        # full_spine,half_spine = spine_pairs[0]
        full_spine = spine_pairs[0][1]
        for _g in dynamic_diagram_generator.generate(d, possible_fields=["aA", "aa", "ad", "dd", "dA"], possible_external_fields="Aa", possible_vertices=["adA"]):
            print _g
            draw_Agraph_with_fields(_g)
        """
        full_spine = ''.join(map(str,full_spine))
        print "Full spine:",full_spine
        internal_nodes = [g for g in G.nodes() if g >= 0]
        NN = []
        for v in internal_nodes:
            print "Node",v
            print "\tNeighbours:",G[v].keys()
            for incident_nodes in G[v].keys():
                # print incident_nodes, G[v][incident_nodes]
                ## for ever edge, even dulicated:
                for u in G[v][incident_nodes].keys():
                    print "\t[v,u]:",(v,incident_nodes)
                    ## if one line is for spine, the another is for dot
                    if ''.join(map(str,[v,u])) in full_spine or ''.join(map(str,[u,v])) in full_spine:
                        G[v][u][0]['spine'] = True
                        print "\tspine!", (v,u)
                        if len(G[v][u])>1:
                            print "\t\tdot!", (v,u)
                            G[v][u][1]['dot'] = True

                        # nG = G.copy()
                        # nG[v][u]['dot'] = v
                        # NN.append(nG)
            #draw_Agraph(G,full_spine,d)
        print "len(NN)",len(NN)
        """