#!/usr/bin/python
# -*- coding: utf8

def ExtractSubgraphs( G, subgraph_list ):
    from graph import Graph, Line

    ctg_lines = set( G.lines.keys() )
    map_reduced_nodes = dict()
    node_types = G.GetNodesTypes()
    cur_node_idx=1000  # номер вершины на который будем заменять вершины текущего  подграфа.
    subgraph_map=dict()
    for idxS in subgraph_list:
        while ( cur_node_idx in node_types):
            cur_node_idx=cur_node_idx+1
        node_types[ cur_node_idx ] = G.model.k_nodetype_r1[ G.subgraphs[idxS].type ]
        subgraph_map[cur_node_idx] = subgraph_list.index(idxS)

        # не факт что K_nodetype хорошее решение.
        
        ctg_lines = ctg_lines - G.subgraphs[idxS].internal_lines
        for idxN in G.subgraphs[idxS].internal_nodes:
            map_reduced_nodes[idxN] = cur_node_idx
        
    ct_graph=Graph(G.model)
    for idxL in ctg_lines:
        if G.lines[idxL].start in map_reduced_nodes:
            In = map_reduced_nodes[ G.lines[idxL].start ] 
        else:
            In = G.lines[idxL].start
        if G.lines[idxL].end in map_reduced_nodes:
            Out = map_reduced_nodes[ G.lines[idxL].end ]
        else:
            Out = G.lines[idxL].end
        ct_graph.AddLine( idxL, Line( G.lines[idxL].type, 
                                     In, Out, G.lines[idxL].momenta, 
                                     G.lines[idxL].dots ) )
    ct_graph.DefineNodes(node_types)
    ct_graph.FindSubgraphs()
    return (ct_graph , subgraph_map)    
        
    
    


class R1Term:
    """ CTGraph - counterterm graph (Graph class)
        SubgraphMap - Map Nodes of CTGraph with appropriate subgraph (dict) 
        subgraphs - tuple of subgraphs (each - Graph class)
    """
    def __init__( self, G, subgraph_list ):
        ( self.ct_graph, self.subgraph_map ) = ExtractSubgraphs( G, subgraph_list )
        self.subgraphs = tuple( [ G.subgraphs[idxS] for idxS in subgraph_list ] )


class R1:
    def __init__( self, G ):

        def IsIntersect( G, subgraph_list ):
            res = False
            lineset=set([])
            int_sub_nodes=set([])
            for idx in subgraph_list:
#                print int_sub_nodes, idx, subgraph_list, G.subgraphs[idx].internal_nodes
                if len( int_sub_nodes & G.subgraphs[idx].internal_nodes ) == 0: # поиск общих вершин
                    int_sub_nodes = int_sub_nodes | G.subgraphs[idx].internal_nodes
                else:
                    return True

                if len( lineset & G.subgraphs[idx].internal_lines) == 0: # поиск общих линий
                    lineset = lineset | G.subgraphs[idx].internal_lines
                else:
                    return True
                                    
            return res

        def xuniqueCombinations( items, n):
            if n == 0: yield [ ]
            else:
                for i in xrange( len( items ) ):
                    for cc in xuniqueCombinations( items[ i+1 : ], n-1 ):
                        yield [ items[ i ] ] + cc            
        
        self.terms = [ ]
        self.terms.append( R1Term( G, [ ] ) )
        for idx in range(1, len( G.subgraphs ) + 1 ):
            
            for subgraph_list in xuniqueCombinations( range( len( G.subgraphs ) ), idx ):
                if not IsIntersect( G, subgraph_list ):
                    self.terms.append( R1Term( G, subgraph_list ) )
                    
    def SaveAsPNG(self, filename):
        from visualization import R12dot
#        import pydot
        gdot=R12dot(self)
        gdot.write_png(filename,prog="dot")            


class Delta:
    pass