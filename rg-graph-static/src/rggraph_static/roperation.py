#!/usr/bin/python
# -*- coding: utf8

def ExtractSubgraph( G, SubgraphList ):
    import copy
    from graph import *
    if len( SubgraphList ) == 0:
        return ( copy.deepcopy( G ), [] )
    CTGLines = set( G.Lines.keys() )
    MapReducedNodes = dict()
    NodeTypes = G.GetNodeTypes()
    CurNodeidx=1000  # номер вершины на который будем заменять вершины текущего  подграфа.
    for idxS in SubgraphList:
        while ( CurNodeidx in NodeTypes):
            CurNodeidx=CurNodeidx+1
        NodeTypes[ CurNodeidx ] = G.model.K_nodetypeR1[ G.subgraphs[idxS].Type ]

        # не факт что K_nodetype хорошее решение.
        
        CTGLines = CTGLines - G.subgraphs[idxS].InternalLines
        for idxN in G.subgraphs[idxS].InternalNodes:
            MapReducedNodes[idxN] = CurNodeidx
            
    CTGraph=Graph(G.model)
    for idxL in CTGLines:
        if G.Lines[idxL].In in MapReducedNodes:
            In = MapReducedNodes[ G.Lines[idxL].In ] 
        if G.Lines[idxL].Out in MapReducedNodes:
            Out = MapReducedNodes[ G.Lines[idxL].Out ]
        CTGraph.AddLine( idxL, Line( G.Lines[idxL].Type, 
                                     In, Out, G.Lines[idxL].Momenta ) )
    CTGraph.DefineNodes(NodeTypes)
    CTGraph.FindSubgraphs()
    return CTGraph    
        
    
    


class R1Term:
    """ CTGraph - counterterm graph (Graph class)
        SubgraphMap - Map Nodes of CTGraph with appropriate subgraph (dict) 
        subgraphs - tuple of subgraphs (each - Graph class)
    """
    def __init__( self, G, SubgraphList ):
        ( self.CTGraph, self.SubgraphMap ) = G.ExtractSubgraphs( SubgraphList )
        self.subgraphs = tuple( [ G.subgraphs[idxS] for idxS in SubgraphList ] )


class R1:
    def __init__( self, G ):

        def IsIntersect( G, SubgraphList ):
            res = False
            lineset=set([])
            intSubNodes=set([])
            for idx in SubgraphList:
                
                if len( intSubNodes & G.subgraph[idx].InternalNodes ) == 0: # поиск общих вершин
                    intSubNodes = intSubNodes | G.subgraph[idx].InternalNodes
                else:
                    return True

                if len( lineset & G.subgraphs[idx].InternalLines) == 0: # поиск общих линий
                    lineset = lineset | G.subgraphs[idx].InternalLines
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
            SubgraphList = xuniqueCombinations( range( len( G.subgraphs ) ), idx )
            if not IsIntersect( G, SubgraphList ):
                self.terms.append( R1Term( G, SubgraphList ) )
            


class Delta:
    pass