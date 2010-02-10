#!/usr/bin/python
# -*- coding: utf8

def ExtractSubgraphs( G, SubgraphList ):
    from graph import Graph, Line
    CTGLines = set( G.Lines.keys() )
    MapReducedNodes = dict()
    NodeTypes = G.GetNodesTypes()
    CurNodeidx=1000  # номер вершины на который будем заменять вершины текущего  подграфа.
    SubgraphMap=dict()
    for idxS in SubgraphList:
        while ( CurNodeidx in NodeTypes):
            CurNodeidx=CurNodeidx+1
        NodeTypes[ CurNodeidx ] = G.model.k_nodetype_r1[ G.subgraphs[idxS].Type ]
        SubgraphMap[CurNodeidx] = SubgraphList.index(idxS)

        # не факт что K_nodetype хорошее решение.
        
        CTGLines = CTGLines - G.subgraphs[idxS].InternalLines
        for idxN in G.subgraphs[idxS].InternalNodes:
            MapReducedNodes[idxN] = CurNodeidx
            
    CTGraph=Graph(G.model)
    for idxL in CTGLines:
        if G.Lines[idxL].start in MapReducedNodes:
            In = MapReducedNodes[ G.Lines[idxL].start ] 
        else:
            In = G.Lines[idxL].start
        if G.Lines[idxL].end in MapReducedNodes:
            Out = MapReducedNodes[ G.Lines[idxL].end ]
        else:
            Out = G.Lines[idxL].end
        CTGraph.AddLine( idxL, Line( G.Lines[idxL].type, 
                                     In, Out, G.Lines[idxL].momenta ) )
    CTGraph.DefineNodes(NodeTypes)
    CTGraph.FindSubgraphs()
    return (CTGraph , SubgraphMap)    
        
    
    


class R1Term:
    """ CTGraph - counterterm graph (Graph class)
        SubgraphMap - Map Nodes of CTGraph with appropriate subgraph (dict) 
        subgraphs - tuple of subgraphs (each - Graph class)
    """
    def __init__( self, G, SubgraphList ):
        ( self.CTGraph, self.SubgraphMap ) = ExtractSubgraphs( G, SubgraphList )
        self.subgraphs = tuple( [ G.subgraphs[idxS] for idxS in SubgraphList ] )


class R1:
    def __init__( self, G ):

        def IsIntersect( G, SubgraphList ):
            res = False
            lineset=set([])
            intSubNodes=set([])
            for idx in SubgraphList:
                print intSubNodes, idx, SubgraphList, G.subgraphs[idx].InternalNodes
                if len( intSubNodes & G.subgraphs[idx].InternalNodes ) == 0: # поиск общих вершин
                    intSubNodes = intSubNodes | G.subgraphs[idx].InternalNodes
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
            
            for SubgraphList in xuniqueCombinations( range( len( G.subgraphs ) ), idx ):
                if not IsIntersect( G, SubgraphList ):
                    self.terms.append( R1Term( G, SubgraphList ) )
    def SaveAsPNG(self, filename):
        from visualization import R12dot
#        import pydot
        gdot=R12dot(self)
        gdot.write_png(filename,prog="dot")            


class Delta:
    pass