#! /usr/bin/python
#! encoding: utf8

__author__ = 'kirienko'

import networkx as nx
from networkx import dijkstra_path_length as dijkstra

from d_to_infty_class import D_to_infty_graph as D


def get_fields(obj,ee):
        """
        Returns fields of edges 'ee' in multigraph U.
        'ee' is a tuple (node1, node2)
        """
        return str(obj.D.edge[ee[0]][ee[1]][ee[2]]['fields'])

def next_edge(cycle_array,_this_edge,_next_node):
    return [e for e in cycle_array if e != _this_edge and _next_node in (e[0],e[1])][0]

def w(x,l):
    """
    w(1,[0,1]) --> 0
    w(0,[0,1]) --> 1
    w(a,[a,b,c,d]) --> b
    @param x: number
    @param l: list of at least two elements, and one of the firsth elements is x (we do not know which one)
    @return: the other of the first two elements (different from x)
    """
    if l[0] == x:  return l[1]
    else: return l[0]

def find_primes(graph_obj):
    nodes = [n for n in graph_obj.D.nodes() if n >=0]
    for n in nodes:
        for n_end,val in graph_obj.D.edge[n].items():
            for elem_k,elem_v in val.items():
                if str(elem_v['fields'])[0] == 'A':
                    # print "\t\t%d <-- prime at "%n,(n,n_end,elem_k)
                    graph_obj.D.add_node(n,prime=(n,n_end,elem_k))
                    graph_obj.U.add_node(n,prime=(n,n_end,elem_k))
                elif str(elem_v['fields'])[1] == 'A':
                    # print "\t\t%d <-- prime at "%n_end,(n,n_end,elem_k)
                    graph_obj.D.add_node(n_end,prime=(n,n_end,elem_k))
                    graph_obj.U.add_node(n_end,prime=(n,n_end,elem_k))
    graph_obj.D.add_node(0,prime=(0,-1,0))
    graph_obj.U.add_node(0,prime=(0,-1,0))

def cycle_from_edges(edges_list):
    G = nx.MultiGraph()
    G.add_edges_from([(e[0],e[1]) for e in edges_list])
    path = [x[0] for x in nx.algorithms.eulerian_circuit(G)]
    # print "\tPath:", " -> ".join(map(str,path))
    P = nx.DiGraph()
    P.add_cycle(path)
    return P

def sign_account(graph_obj):
    # print "\ndiag No",diag_dict[graph_obj.nickel]
    sign = -1
    ## get cycles with momenta
    cycles = dict()
    arr = [(x,graph_obj.momenta_in_edge(x)) for x in graph_obj.U.edges_iter(keys=True)]
    for i in xrange(graph_obj.Loops):
        cycles.update({"k%d"%i:[e[0] for e in arr if 'k%d'%i in e[1]]})

    find_primes(graph_obj)

    ## go around the bridges
    for b in graph_obj.bridges:
        # print "Bridge",b
        m0,m1 = [set(graph_obj.momenta_near_node(x)) for x in b]
        momenta = m0.intersection(m1)

        for mom in momenta:
            path_graph = cycle_from_edges(cycles[mom])
            ## edges at node which have fields 'phiprime':
            primes = [graph_obj.U.node[x]['prime'] for x in b]
            t0,t1 = [(b[x], w(b[x],primes[x])) for x in [0,1]]
            # print "\tat the end of the bridge b[0]: %d --> %d"%(t0)
            # print "\tat the end of the bridge b[1]: %d --> %d"%(t1)
            if dijkstra(path_graph,*t0) != dijkstra(path_graph,*t1):
                sign *= -1
                # print "\tSIGN CHANGED"
                break
    return sign
    

if  __name__ == "__main__":
    Loops = 3
    from ours_VS_vasya import diag_dict
    with open('%dloop_nonzero.txt'%Loops) as fd:
       str_diags = [d.strip() for d in fd.readlines()]

    vasya = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aa|aA_dd||' # No 1
    one   = 'e12|e3|34|5|55||:0A_dd_aA|0a_Aa|dd_aA|Aa|aA_dd||' # one time version -- No 18
    d25   = 'e12|e3|45|45|5||:0A_aA_dA|0a_dA|aa_dd|dd_aA|Aa||'

    d5  = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aA|aa_dd||'
    d48 = 'e12|23|4|45|5|e|:0A_aA_dA|dd_aA|aA|dd_aA|ad|0a|'
    d77 = 'e12|23|4|e5|55||:0A_aA_dA|dd_aA|aA|0a_dA|aa_dd||'

    # v = D(d25)
    # sign_account(v)
    diags = [D(x) for x in str_diags if int(diag_dict[x])]
    signs = dict([(int(diag_dict[diag.nickel]),sign_account(diag)) for diag in diags])


    for diag in sorted(signs.keys()):
        print diag,
        # s = sign_account(diag)
        if signs[diag] == -1:
            print "minus"
        else:
            print
