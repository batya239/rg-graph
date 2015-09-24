#! /usr/bin/python
#! encoding: utf8

__author__ = "kirienko"

import graph_state as gs
import networkx as nx
from copy import deepcopy
import graphine, graph_state_config_with_fields
import itertools as it
#import dynamic_diagram_generator

## Filters
connected = graphine.filters.connected
oneIR = graphine.filters.one_irreducible
@graphine.filters.graph_filter
def self_energy(sub_graph_edges, super_graph):
    """
    Filter for self-energy subgraphs (with 2 external legs)
    """
    if len(sub_graph_edges):
        if len([e for e in sub_graph_edges if e.is_external()])==2:
            return True
    return False

def test(seq,rules):
    for comp in rules:
        if False in map(lambda (x,y):seq.index(x)<seq.index(y),comp):
            return
    return seq

def is_significant_subgraph(sg,tv):
    """
    Returns True if subgraph 'sg' is significant for time version 'tv',
        False otherwise.
    Significance means that all nodes of subgraph appear in the time version
    sequentially, with no breakage (the order of nodes does not matter).
    E.g. for the time version [0,1,2,3,4,5] the subgraph [3,2,4] is significant,
    whereas [2,4,5] is not.
    """
    for i,v in enumerate(tv):
        if v in sg:
            if sorted(tv[i:i+len(sg)]) == sg:
                return True
            else:
                return False

class D_to_infty_graph():
    def __init__(self,nickel_str):
        self.nickel = nickel_str
        self.Loops = graph_state_config_with_fields.from_str(self.nickel).loops_count
        self.D = self.nx_graph_from_str(nickel_str)
        self.U = self.D.to_undirected()
        if self.is_zero():
            print "Diagram has zero value"

    def __str__(self):
        return self.nickel

    def nx_graph_from_str(self, nickel_str):
        """
        Returns networkx MultiGraph object from Nickel string
        NB: here we 'forget' about graph_state ancestry
        """
        if not ":" in str(nickel_str):
            gs_diag = self.static_diag(nickel_str)
            edges = [tuple(map(lambda n: n.index, e.nodes)) for e in gs_diag.edges]
            ext = [e for e in edges if -1 in e]
            ext_index = lambda x: 1-x.index(-1)
            g = nx.MultiGraph()

            for i,e in enumerate(ext):
                    edges.remove(e)
                    edges.append((e[ext_index(e)],-i-1))
            g.add_edges_from(edges)

        else:
            gs_diag = self.dynamic_diag(nickel_str)
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

    @staticmethod
    def static_diag(diag_from_str):
        sc = gs.PropertiesConfig.create()
        return sc.graph_state_from_str(diag_from_str)

    @staticmethod
    def dynamic_diag(diag_from_str):
        sc = gs.PropertiesConfig.create(
                    gs.PropertyKey(name="fields",
                                    is_directed=True,
                                    externalizer=gs.Fields.externalizer()))
        return sc.graph_state_from_str(diag_from_str)

    @staticmethod
    def is_phiphi(fields):
        """
        Returns True if array 'fields' contains
        at least one of ["aa","dd","ad","da"],
        False -- elsewise
        """
        return bool(filter(lambda x:x in ["aa","dd","ad","da"],fields))

    def get_fields(self,ee):
        """
        Returns fields of edges 'ee' in multigraph U.
        'ee' is a tuple (node1, node2)
        """
        return map(lambda x:str(x.get('fields')),self.U.edge[ee[0]][ee[1]].values())

    def find_simple_momenta(self):
        """
        Returns pairs (edge,field) where 'edge'
        corresponds to simple momentum
        """
        ans = set()
        counter = 1
        edges = set([(e1,e2) for e1,e2 in self.U.edges_iter()])
        for e1,e2 in edges:
            #print (e1,e2)
            if not (e1<0 or e2<0):
                fields = [(k,v['fields']) for k,v in self.U.edge[e1][e2].items()]
                #print "fields:",fields
                for f in fields:
                    if self.is_phiphi([str(f[1])]):
                        ans.add(((e1,e2,f[0]),f))
                        if counter <= self.Loops:
                            self.U.add_edge(e1,e2,f[0],mom=int("0"*counter+"1"+"0"*(self.Loops-counter),2))
                            #print "Add mom","0"*counter+"1"+"0"*(Loops-counter)," at",(e1,e2,f[0])
                        counter += 1
            elif e1<0 or e2<0:
                self.U.add_edge(e1,e2,0,mom=int("1"+"0"*self.Loops,2))
        return list(ans)

    def subgraph_simple_momenta(self,gs_subgraph):
        """
        :param gs_subgraph: graphine subgraph
        :return: list of internal (for this subgraph) momenta, i.g. ['k1','k3']
        """
        internal_nodes = [x for x in gs_subgraph.vertices if x>-1]
        all_simple_momenta = set([m[0] for m in self.find_simple_momenta()])
        subgraph_edges     = set(self.U.subgraph(internal_nodes).edges(keys=True))
        simple_edges       = all_simple_momenta.intersection(subgraph_edges)
        return map(lambda x: self.momenta_in_edge(x)[0],simple_edges)


    def is_zero(self):
        """
        Returns True if diag 'name' has zero value,
        False otherwise.
        """
        ## find simple momenta
        self.find_simple_momenta()

        ## find independent cycles with simple momenta
        self.find_cycles()
        ## copy momenta to undirected graph:
        #[[Z[e1][e2][k]['mom'] for k in Z[e1][e2]] for e1,e2 in Z.edges_iter()]
        for e1,e2 in self.D.edges_iter():
            for k in self.D[e1][e2]:
                self.D.add_edge(e1,e2,k,mom=self.U[e1][e2][k]['mom'])
        
        ## find 'bridges'
        for i in xrange(len(self.D.nodes())-2):
            self.flow_near_node(i)
        
        self.U = self.D.to_undirected()
        ## test bridges over cycles
        self.bridges = self.find_bridges()
        for b in self.bridges:
            test = map(lambda x: int(self.flow_near_node(x),2),b)
            if not test[0] & test[1]:
                return True
        return False

    def find_cycles(self):
        """
        Black magic explained:
        Here we go through the internal nodes (= all nodes except 2) and
        search for such ones that have TWO [of 3] edges with
        the property 'mom[entum]' defined. Then we can define 'mom' on the third edge
        as mom3 = mom1 XOR mom2
        In the end 'mom' is defined on the every edge.
        """

        # nodp = number of defined properties in each node:
        nodp = [sum([sum(map(len,v.values())) for v in self.U[i].values()]) for i in range(len(self.U.node)-2)]
        while 5 in nodp:
            ## 5 means that such a node has 2 of 3 edges with 'mom' defined
            cur_node = nodp.index(5)
            #print "Current node:",cur_node
            mom_map = [(k,map(len,v.values())) for k,v in self.U[cur_node].items()]
            #print "mom_map =",mom_map
            for elem in mom_map:
                if 1 in elem[1] :# 1 means that 'mom' is undefined for such an edge
                    #print "from_node = %d, to_node = %d"%(cur_node,elem[0])
                    #print self.U[cur_node][elem[0]]
                    ## edges with already defined 'mom's
                    m = list(set(self.U[cur_node].keys())-set([elem[0]]))
                    #print "m =",m
                    if len(m) == 2:
                        mom1 = self.U[cur_node][m[0]].values()[0]['mom']
                        mom2 = self.U[cur_node][m[1]].values()[0]['mom']
                    elif len(m) == 1 and (len(mom_map)>2 or sum(elem[1])>1): # <-- 'mom' is already defined at
                        m = self.U[cur_node].keys()                       # one of two edges between 'from-to' nodes
                        #print "new m =",m
                        line_num_1 = [k for k,v in self.U[cur_node][m[0]].items() if 'mom' in v.keys()][0]
                        line_num_2 = [k for k,v in self.U[cur_node][m[1]].items() if 'mom' in v.keys()][0]
                        mom1 = self.U[cur_node][m[0]].values()[line_num_1]['mom']
                        mom2 = self.U[cur_node][m[1]].values()[line_num_2]['mom']
                    elif len(m) == 1 and len(mom_map)==2 and sum(elem[1])==1:# <-- 'mom's are already defined at
                              # two edges between the same nodes
                        mom1 = self.U[cur_node][m[0]][0]['mom']
                        mom2 = self.U[cur_node][m[0]][1]['mom']

                    else:
                        raise
                    line_num =  map(len,self.U[cur_node][elem[0]].values()).index(1)
                    #print "\tmom1 =",mom1,",\tmom2 =",mom2,",\tmom1^mom2 =",bin(mom1^mom2)
                    self.U.add_edge(cur_node,elem[0],line_num,mom=mom1^mom2)
                    nodp = [sum([sum(map(len,v.values())) for v in self.U[i].values()]) for i in range(len(self.U.node)-2)]
        return

    def find_bridges(self):
        """
        Returns pairs of nodes that are connected by bridges:
        [(0,1),(2,3),(4,5)]
        """
        fields = lambda x: self.U[x[0]][x[1]][x[2]]['fields']
        bridges = []
        for i in xrange(len(self.U.nodes())-2):
            # print "\ni = %d"%i
            cur_edge = (i,self.U.node[i]['dot'][0],self.U.node[i]['dot'][1])
            # print "Current edge:", cur_edge
            bridges += [[cur_edge]]
            if str(fields(cur_edge)) == 'dd':
                continue
            while True:
                next_node = cur_edge[1]
                #print "next node: %d"%next_node
                next_lines= deepcopy(self.U[next_node])
                #print "next lines:",next_lines
                next_lines[cur_edge[0]].pop(cur_edge[2])
                dot = self.U.node[next_node]['dot']
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
        # print "bridges:", bridges
        for b in bridges:
            bridge_set.add(tuple(sorted([b[0][0],b[-1][1]])))
        return list(bridge_set)

    def flow_near_node(self,node):
        """
        Returns the number of simple momenta that flows through the node
        by the dotted edge (binary string like '0100').
        For directed graphs only.
        """
        mom = []
        pr = self.D.predecessors(node)
        for n in pr:
            for nn in self.D[n][node]:
                if 'd' == self.D[n][node][nn]['fields'][-1]:
                    self.D.add_node(node,dot = (n,nn))
                    continue
                mom += [self.D[n][node][nn]['mom']]
        to_nodes = self.D.successors(node)
        for n in to_nodes:
            for nn in self.D[node][n]:
                if 'd' == self.D[node][n][nn]['fields'][0]:
                    self.D.add_node(node,dot = (n,nn))
                    continue
                mom += [self.D[node][n][nn]['mom']]

        return bin(mom[0] & mom[1])[2:]

    def momenta_near_node(self,node):
        """
        The same as 'flow_near_node', but returns the list of momenta.
        """
        binary_mom = self.flow_near_node(node)
        return ["k%d"%j for j,k in enumerate(binary_mom[::-1]) if int(k) and j < self.Loops]

    def momenta_in_edge(self,e):
        """
        :param G: networkx MultiGraph
        :param edge: (e0,e1,e2)
        :return: the list of momenta, i.e. ['k0','k2','k3']
        """
        mom = self.U[e[0]][e[1]][e[2]]['mom']
        return ["k%d"%j for j,k in enumerate(bin(mom)[:1:-1]) if int(k) and j < self.Loops]
    
    def get_time_versions(self):
        """
        Returns all time versions of a graph G with Nickel representation 'nickel_str',
            along with all significant subgraphs that correspond every time version:
        >>> z = D_to_infty_graph("e12|e3|34|5|55||:0A_dd_aA|0a_Aa|dd_aA|Aa|aA_dd||")
        >>> z.get_time_versions()
        [([0, 2, 4, 5, 3, 1], [e11|e|:0A_aA_dd|0a|, e12|e3|33||:0A_dd_aA|0a_Aa|aA_dd||])]

        Also creates self.tv = self.get_time_versions()
        Directed edges in our diagram form directed acyclic graph (DAG) with a root 'root'.
        
        """
        T =  nx.DiGraph()
        for e1 in self.U.edge:   
            for e2 in self.D.edge[e1]:
                for k in self.D[e1][e2]:
                    if 'A' in self.D[e1][e2][k]['fields']:
                        idx = str(self.D[e1][e2][k]['fields']).index('A')
                        from_node = (e1,e2)[1-idx]
                        to_node   = (e1,e2)[idx] 
                        T.add_edge(from_node,to_node)
        ## Find all self-energy subgraphs
        G = graph_state_config_with_fields.from_str(self.nickel)
        subgraphs = [x for x in G.x_relevant_sub_graphs(filters=connected+oneIR+self_energy)]
        sg_nodes  = [sorted([v for v in sg.vertices if v>0]) for sg in subgraphs]
    
        ## Find the root of DAG:
        root   = [i for i in T.node if T.in_degree(i) == 0][0] 
        if root < 0:
            T.remove_node(root)
            root = [i for i in T.node if T.in_degree(i) == 0][0] 
        ## Nodes of DAG:
        nodes = list(set(T.nodes())-set([root]))
        ## Leaves of DAG:
        leaves = [l for l in T.nodes() if T.out_degree(l)==0]   
        ## Find all paths from root to every leaf:
        paths = []
        for i in leaves:
            paths += [i for i in nx.algorithms.all_simple_paths(T,root,i)]
        ## Comparison rules for every two nodes that define whether
        ##      time version is correct: 
        test_cmp = [[i for i in it.combinations(p,2)] for p in paths]
        ## Find all possible permutations of nodes   
        perm = [[root]+list(i) for i in it.permutations(nodes,len(nodes))]
        ## Apply the rules of comparison
        vers = []
        for p in perm:
            ver = test(p,test_cmp)
            if ver:
                ## Test if subgraph is significant for this time version
                vers += [(ver,\
                    [subgraphs[i] for i, sg in enumerate(sg_nodes) if
                        is_significant_subgraph(sg,ver)
                     and '0A' in str(subgraphs[i])
                     and '0a' in str(subgraphs[i])])]
        self.tv = vers
        return vers