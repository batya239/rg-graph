#!/usr/bin/python
# -*- coding: utf8


class R1Term:
    """ CTGraph - counterterm graph (Graph class)
        SubgraphMap - Map Nodes of CTGraph with appropriate subgraph (dict) 
        subgraphs - tuple of subgraphs (each - Graph class)
    """
    def __init__( self, G, SubgraphList ):
        ( self.CTGraph, self.SubgraphMap ) = G.ExtractSubgraphs( SubgraphList )
        self.subgraphs=tuple( [ G.subgraphs[idxS] for idxS in SubgraphList ] )


class R1:
    def __init__( self, G ):

        def IsIntersect( G, SubgraphList ):
            res = True
            lineset=set([])
            for idx in SubgraphList:
                if len( lineset & G.subgraphs[idx].InternalLines) == 0:
                    lineset = lineset | G.subgraphs[idx].InternalLines
                else:
                    res = False
                    break
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