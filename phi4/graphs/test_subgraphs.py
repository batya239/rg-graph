#!/usr/bin/python
# -*- coding:utf8
from nose.tools import raises

import subgraphs

from lines import Line
from nodes import Node
from graphs import Graph

class _model():
    def __init__( self , name):
        self.name=name
        self.space_dim=6
        self.lines_dim={1:-2}
        self.modifiers_dim={'tau':-2,'p':-1}
        self.nodes_dim={1:0}
    def Dim( self, obj ):
        if obj.type==None:
            raise ValueError , "cant determine Dim: type is None"
        if isinstance( obj, Line ):
            dim=self.lines_dim[obj.type]
        elif isinstance( obj, Node):
            dim=self.nodes_dim[obj.type]
        else:
            raise ValueError, 'unknown object'
        if obj.modifiers<>None:
            for mod in obj.modifiers:
                    dim+=self.modifiers_dim[mod]
        return dim
    def SetTypes(self, graph):
        """ set types for graph nodes and lines ( this implementation may be used only for models with 1 type of lines and 1 type of nodes)
        """
        for line in graph.xInternalLines():
            line.type=1
        for node in graph.xInternalNodes():
            node.type=1
        

class _phi4():
    def __init__( self , name):
        self.name=name
        self.space_dim=4
        self.lines_dim={1:-2}
        self.modifiers_dim={'tau':-2,'p':-1}
        self.nodes_dim={1:0}
    def Dim( self, obj ):
        if obj.type==None:
            raise ValueError , "cant determine Dim: type is None"
        if isinstance( obj, Line ):
            dim=self.lines_dim[obj.type]
        elif isinstance( obj, Node):
            dim=self.nodes_dim[obj.type]
        else:
            raise ValueError, 'unknown object'
        if obj.modifiers<>None:
            for mod in obj.modifiers:
                    dim+=self.modifiers_dim[mod]
        return dim

    def SetTypes(self, graph):
        """ set types for graph nodes and lines ( this implementation may be used only for models with 1 type of lines and 1 type of nodes)
        """
        for line in graph.xInternalLines():
            line.type=1
        for node in graph.xInternalNodes():
            node.type=1
        

class test_Dim():
    def setUp(self):
        self.model=_model('phi3')
        self.g=Graph('e11-e-')
        self.g1=Graph('e11-e-')
        self.model.SetTypes(self.g1)
        self.g2=Graph('e12-e3-33-')
        self.model.SetTypes(self.g2)
        self.g3=Graph('e12-e2-e-')
        self.model.SetTypes(self.g3)



    @raises(ValueError)
    def test_DimNodeNone(self):
        for node in self.g.xInternalNodes():
            res=node.Dim(self.model)
            break

    @raises(ValueError)
    def test_DimLineNone(self):
        for line in self.g.xInternalLines():
            res=line.Dim(self.model)
            break

    def test_DimNode(self):
        for node in self.g1.xInternalNodes():
            print  node.Dim(self.model), 0
            assert node.Dim(self.model) == 0
            

    def test_DimLineNone(self):
        for line in self.g1.xInternalLines():
            assert line.Dim(self.model) == -2

    def test_DimGraph(self):
        print self.g1.Dim(self.model), 2
        assert self.g1.Dim(self.model)==2
        assert self.g2.Dim(self.model)==2
        assert self.g3.Dim(self.model)==0

    def test_DimSubgraph(self):
        lines=[x.idx() for x in self.g3.xInternalLines()]
        assert subgraphs.Dim(lines[0:2],self.model)==-4

class test_subgraphs:
    def setUp(self):
        self.g=Graph('e12-e3-33-')
        self.model=_model('phi3')
        self.model.SetTypes(self.g)
        self.phi4=_phi4('phi4')

    

    def test_FindSubgraphs(self):
        def findsubgraphs(nickel,model):
            g=Graph(nickel)
            model.SetTypes(g)
            res=[]
            for sub in subgraphs.FindSubgraphs(g,model):
                g1=Graph(subgraphs.ToEdges(sub))
                g1.GenerateNickel()
                res.append(str(g1.nickel))
            res.sort()
            return res

        assert findsubgraphs('e12-e3-33-',self.model) == ['e11-e-']

        assert findsubgraphs('e12-e3-34-5-e6-67-8-88--',self.model) == ['e11-e-', 'e12-e3-33--', 'e12-e3-e4-45-6-66--']

        assert findsubgraphs('e111-e-',self.phi4) == ['ee11-ee-','ee11-ee-','ee11-ee-']

        assert findsubgraphs('ee12-223-3-ee-',self.phi4)==['ee11-ee-','ee12-e22-e-','ee12-e22-e-',]


    def findsub(self,g):
            """ find first simple subgraph e11-e-
            """
            for node in g.xInternalNodes():
                out_nodes=node.OutNodes()
                reverse=dict()
                for line in out_nodes.keys():
                    if out_nodes[line] not in reverse.keys():
                        reverse[out_nodes[line]]=line
                    else:
                        return (line,reverse[out_nodes[line]])
    
#     def test_FindExternal(self):
#         nodes,lines= subgraphs.FindExternal(self.findsub(self.g))
#         print self.findsub(self.g)
#         print [x.idx() for x in nodes], lines
#         print self.g._edges()
# 
#         assert False

    def test_ToEdges(self):
        print self.findsub(self.g) , self.g._lines
        print subgraphs.ToEdges(self.findsub(self.g))
        g1=Graph(subgraphs.ToEdges(self.findsub(self.g)))
        g1.GenerateNickel()
        assert str(g1.nickel)=='e11-e-'

