#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

from networkx import MultiGraph
from numpy import array
from itertools import product
from copy import deepcopy
import dynamic_diagram_generator

from spine import nx_graph_from_str

def find_simple_momenta(G):
    """
    Returns pairs (edge,field) where 'edge'
    corresponds to simple momentum
    """
    #print
    ans = set()
    counter = 1
    edges = set([(e1,e2) for e1,e2 in G.edges_iter()])
    for e1,e2 in edges:
        #print (e1,e2)
        if not (e1<0 or e2<0):
            fields = [(k,v['fields']) for k,v in G.edge[e1][e2].items()]
            #print "fields:",fields
            for f in fields:
                if is_phiphi([str(f[1])]):
                    ans.add(((e1,e2,f[0]),f))
                    if counter <= Loops:
                        G.add_edge(e1,e2,f[0],mom=int("0"*counter+"1"+"0"*(Loops-counter),2))
                        #print "Add mom","0"*counter+"1"+"0"*(Loops-counter)," at",(e1,e2,f[0])
                    counter += 1
        elif e1<0 or e2<0:
            G.add_edge(e1,e2,0,mom=int("1"+"0"*Loops,2))
    return list(ans)

def get_fields(G,ee):
    """
    Returns fields of edges 'ee' in multigraph G.
    'ee' is a tuple (node1, node2)
    """
    return map(lambda x:str(x.get('fields')),G.edge[ee[0]][ee[1]].values())

def is_phiphi(fields):
    """
    Returns True if array 'fields' contains 
    at least one of ["aa","dd","ad","da"],
    False -- elsewise
    """
    return bool(filter(lambda x:x in ["aa","dd","ad","da"],fields))

def is_phiprime(fields):
    """
    Returns True if array 'fields' contains 
    at least one of ["aA","Aa","Ad","dA"],
    False -- elsewise
    """
    return bool(filter(lambda x:x in ["aA","Aa","Ad","dA"],fields))

def get_boundary_nodes(path):
    #nodes = set(array(path).flatten()) # set of nodes from edges list
    S = MultiGraph()
    S.add_edges_from(path)
    return [i[0] for i in S.degree_iter() if i[1]==1]

def phiprime_neighbours(G,path):
    """
    Returns such edges that
    1) neighbours of path's boundary nodes
    2) have only phi-prime fields
    """
    all_nodes = set(array(path).flatten())
    edge = get_boundary_nodes(path)
    internal_nodes = all_nodes - set(edge)
    #print "Boundary nodes = ",edge
    if len(edge) == 0:
        return []
    set0 = set(G.neighbors(edge[0]))-internal_nodes
    set1 = set(G.neighbors(edge[1]))-internal_nodes
    nei1, nei2 = product(set0,[edge[0]]), product(set1,[edge[1]])
    return [[i for i in nei1 if is_phiprime(get_fields(G,i))], \
            [i for i in nei2 if is_phiprime(get_fields(G,i))]]

def find_cycles(G):
    ## Black magic explained:
    ## Here we go through internal nodes (= all nodes except 2) and
    ## search for such ones that have TWO [of 3] edges with 
    ## property 'mom[entum]' defined. Then we can define 'mom' on the third edge
    ## as mom3 = mom1 XOR mom2
    ## In the end 'mom' is defined on every edge.

    # nodp = number of defined properties in each node:
    nodp = [sum([sum(map(len,v.values())) for v in G[i].values()]) for i in range(len(G.node)-2)]
    while 5 in nodp:
        ## 5 means that such a node has 2 of 3 edges with 'mom' defined
        cur_node = nodp.index(5)
        #print "Current node:",cur_node
        mom_map = [(k,map(len,v.values())) for k,v in G[cur_node].items()]
        #print "mom_map =",mom_map
        for elem in mom_map:
            if 1 in elem[1] :# 1 means that 'mom' is undefined for such an edge
                #print "from_node = %d, to_node = %d"%(cur_node,elem[0])
                #print G[cur_node][elem[0]]
                ## edges with already defined 'mom's
                m = list(set(G[cur_node].keys())-set([elem[0]]))
                #print "m =",m
                if len(m) == 2:
                    mom1 = G[cur_node][m[0]].values()[0]['mom']
                    mom2 = G[cur_node][m[1]].values()[0]['mom']
                elif len(m) == 1 and (len(mom_map)>2 or sum(elem[1])>1): # <-- 'mom' is already defined at 
                    m = G[cur_node].keys()                       # one of two edges between 'from-to' nodes
                    #print "new m =",m
                    line_num_1 = [k for k,v in G[cur_node][m[0]].items() if 'mom' in v.keys()][0]
                    line_num_2 = [k for k,v in G[cur_node][m[1]].items() if 'mom' in v.keys()][0]
                    mom1 = G[cur_node][m[0]].values()[line_num_1]['mom']
                    mom2 = G[cur_node][m[1]].values()[line_num_2]['mom']
                elif len(m) == 1 and len(mom_map)==2 and sum(elem[1])==1:# <-- 'mom's are already defined at 
                          # two edges between the same nodes
                    mom1 = G[cur_node][m[0]][0]['mom']
                    mom2 = G[cur_node][m[0]][1]['mom']
                    
                else:
                    raise
                line_num =  map(len,G[cur_node][elem[0]].values()).index(1)
                #print "\tmom1 =",mom1,",\tmom2 =",mom2,",\tmom1^mom2 =",bin(mom1^mom2)
                G.add_edge(cur_node,elem[0],line_num,mom=mom1^mom2)
                nodp = [sum([sum(map(len,v.values())) for v in G[i].values()]) for i in range(len(G.node)-2)]
    return

def flow_near_node(G,node):
    """
    Returns number of simple momenta that flows through the node
    by the dotted edge (binary string like '0100').
    For directed graphs only.
    """
    mom = []
    pr = G.predecessors(node)
    for n in pr:
        for nn in G[n][node]:
            if 'd' == G[n][node][nn]['fields'][-1]:
                G.add_node(node,dot = (n,nn))
                continue
            mom += [G[n][node][nn]['mom']]
    to_nodes = G.successors(node)
    for n in to_nodes:
        for nn in G[node][n]:
            if 'd' == G[node][n][nn]['fields'][0]:
                G.add_node(node,dot = (n,nn))
                continue
            mom += [G[node][n][nn]['mom']]

    return bin(mom[0] & mom[1])[2:]

def find_bridges(G):
    """
    Returns list of paths from 'point' to 'point' in a way
    [node_0, node_1, ..., node_n]
    """
    fields = lambda x: G[x[0]][x[1]][x[2]]['fields']
    bridges = []
    for i in xrange(len(G.nodes())-2):
        #print "\ni = %d"%i
        cur_edge = (i,G.node[i]['dot'][0],G.node[i]['dot'][1]) 
        #print "Current edge:", cur_edge
        bridges += [[cur_edge]]
        if str(fields(cur_edge)) == 'dd':
            continue
        while True:
            next_node = cur_edge[1]
            #print "next node: %d"%next_node
            next_lines= deepcopy(G[next_node])
            #print "next lines:",next_lines
            next_lines[cur_edge[0]].pop(cur_edge[2])
            dot = G.node[next_node]['dot']
            next_lines[dot[0]].pop(dot[1])
            for (k,v) in next_lines.items():
                if len(v) == 0:
                    next_lines.pop(k)
            #print "next lines:",next_lines
            nce1 = next_lines.keys()[0]
            nce2 = next_lines[nce1].keys()[0]
            cur_edge = (next_node,nce1,nce2)
            bridges[-1] += [cur_edge]
            if 'd' in str(fields(cur_edge)):
                break
    bridge_set = set()
    for b in bridges:
        bridge_set.add(tuple(sorted([b[0][0],b[-1][1]])))
    return list(bridge_set)

def is_zero(name):
    """
    Returns True if diag 'name' has zero value,
    False otherwise.
    """
    U = nx_graph_from_str(name)

    Z = U.to_undirected()
    ## find simple momenta
    simple_momenta = find_simple_momenta(Z)

    ## find independent cycles with simple momenta
    find_cycles(Z)
    ## copy momenta to undirected graph:
    #[[Z[e1][e2][k]['mom'] for k in Z[e1][e2]] for e1,e2 in Z.edges_iter()]
    for e1,e2 in U.edges_iter():
        for k in U[e1][e2]:
            U.add_edge(e1,e2,k,mom=Z[e1][e2][k]['mom'])
    
    ## find 'bridges'
    for i in xrange(len(U.nodes())-2):
        flow_near_node(U,i)
    
    Z = U.to_undirected()
    ## test bridges over cycles
    bridges = find_bridges(Z)
    for b in bridges:
        test = map(lambda x: int(flow_near_node(U,x),2),b)
        if not test[0] & test[1]:
            return True
    return False


if  __name__ == "__main__":
    Loops = 5
    with open('%dloop_all.txt'%Loops) as fd:
    #with open("../e2-%dloop.txt.gs"%Loops) as fd:
        diags = [d.strip() for d in fd.readlines()]
    vasya = 'e12|e3|34|5|55||:0A_aA_dA|0a_dA|dd_aA|aa|aA_dd||'
    zero = []
    nonzero = []
    
    #for d in diags:
    for j,name in enumerate(diags):
            name = str(name)
            #print "%d) %s "%(j, name),
            try:
                zz = is_zero(name)
            except:
                zz = True
            #if is_zero(name):
            if zz:
                #print "has zero value"
                zero += [name]
            else:
                #print
                nonzero += [name]
    types = list(set([d.split(':')[0] for d in nonzero]))
    for t in types:
        print t,len([d for d in nonzero if t==d.split(':')[0]])

    with open('%dloop_nonzero.txt'%Loops,'w') as fd:
        for d in nonzero:
            fd.write(d+'\n')
