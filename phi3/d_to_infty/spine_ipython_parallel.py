#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

import graph_state as gs
import networkx as nx
import itertools as it
import dynamic_diagram_generator
from IPython.parallel import Client
import os, sys

## Convert GraphState.edge --> tuple
edge_to_ints = lambda e: tuple(map(lambda n: n.index, e.nodes))

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
        ext = [e for e  in gs_diag.edges if e.is_external()]

        g = nx.MultiDiGraph()
        for e in edges:
            i,j = tuple(map(lambda n: n.index, e.nodes))
            g.add_edge(i,j,fields = e.fields)
        for k,e in enumerate(ext):
            i,j = tuple(map(lambda n: n.index, e.nodes))
            g.add_edge(-k-1,j,fields = e.fields)
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
    ## Find all possible path between 'source' and 'sink'
    all_paths = [p for p in nx.all_simple_paths(G,source,sink)]
    ## for every pair of paths:
    for s in it.combinations(all_paths,2):
        ## find all pairs that have no intersections except for edge nodes
        if set(s[0][1:-1]).intersection(set(s[1][1:-1])) == set():
            spine_pairs.append(s)
            # print s,type(s)
    new_spine_pairs = []
    for elem in spine_pairs:
        if elem not in new_spine_pairs:
            new_spine_pairs.append(elem)
    return new_spine_pairs

def direct(edge,graphine_edge):
        """
        Returns inversed field if directions of 'edge' and 'graphine_edge' are different
        """
        if edge == tuple(map(lambda n: n.index, graphine_edge.nodes)):
            return str(graphine_edge.fields)
        else:
            return str(graphine_edge.fields)[::-1]


def filter_spines(G,spines):
    """
    @param G:
    @param spines:
    @return: True if graph G has spine from 'spines'
    """
    for spine in spines:
        for j,path in enumerate(spine):
            ## walk through spine
            chain = [(path[i],path[i+1]) for i in xrange(len(path)-1)]
            path_fields = [ direct(e,G.edges(*e)[0]) for e in chain]
            if path_fields.count('aA') == len(path)-1:
                another_path = spine[j-1]
                chain = [(another_path[i],another_path[i+1]) for i in xrange(len(another_path)-1)]
                path_fields = [ direct(e,G.edges(*e)[0]) for e in chain]
                # print another_path,path_fields
                if len(path_fields) == 1 and path_fields[0] == 'dd':
                                # print "\t\tRail 2:",another_path, path_fields
                                return True
                elif len(path_fields) > 1 and path_fields[0] in ['dA','da']:
                    if path_fields[-1] in ['Ad','ad']:
                        if len(path_fields) == 2:
                            return True
                        elif len(path_fields) > 2:
                            if path_fields.count('aA') + \
                                    path_fields.count('Aa') + \
                                    path_fields.count('aa') == len(path_fields)-2:
                                # print "\t\tRail 2:",another_path, path_fields
                                return True
                        else:
                            print "Something went wrong"
                            raise

def get_dyn_diags(diag_str):
    import os
    os.chdir(os.path.expanduser('~')+'/rg-graph/phi3/d_to_infty/')
    from spine_ipython_parallel import nx_graph_from_str, spine, filter_spines,dynamic_diagram_generator
    print "\n",diag_str
    G = nx_graph_from_str(diag_str)
    source = 0
    sink = max([g for g in G.edges() if g[1] < 0])[0]
    spine_pairs = spine(G,source,sink)+spine(G,sink,source)
    
    local_counter_all = 0
    local_good        = []
    for _g in dynamic_diagram_generator.generate(diag_str, possible_fields=["aA", "aa", "ad", "dd", "dA"], possible_external_fields="Aa", possible_vertices=["adA"]):
        local_counter_all +=1
        if filter_spines(_g,spine_pairs):
            local_good += [_g]
    #print "All: %d, good:dd %d"%(local_counter_all,len(local_good))

    return local_counter_all, len(local_good)
    
if  __name__ == "__main__":
    Loops = 2
    with open("../e2-%dloop.txt.gs"%Loops) as fd:
        diags = [d.strip() for d in fd.readlines()]
    path = os.path.expanduser('~')+'/rg-graph/phi3/d_to_infty/'
    loop_path = path + 'diags_%d_loops'%Loops
    if not os.path.exists(loop_path):
        os.mkdir(loop_path) 
        print "Created: %s"%loop_path
    
    rc = Client() # <-- ipcluster MUST be started at this moment
    print rc.ids
    lview = rc.load_balanced_view() # default load-balanced view

    res = lview.map(get_dyn_diags,diags,block=True)
    print res

    count_all = sum([i[0] for i in res])
    count_good= sum([i[1] for i in res])
    """
        for _g in dynamic_diagram_generator.generate(d, possible_fields=["aA", "aa", "ad", "dd", "dA"], possible_external_fields="Aa", possible_vertices=["adA"]):
            # print "_"*5
            count_all +=1
            if filter_spines(_g,spine_pairs):
                print _g
                good_list += [_g]
    """
    print "_"*30+"\nAll: %d, good: %d"%(count_all, count_good)
    #with open('%dloop_all.txt'%Loops,'w') as fd:
    #    for g in good_list:
    #        fd.write(str(g)+'\n')
