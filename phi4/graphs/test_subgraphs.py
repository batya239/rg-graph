#!/usr/bin/python
# -*- coding:utf8
from nose.tools import raises

import subgraphs


from graphs import Graph

from dummy_model import _phi3,_phi4
        

class test_Dim():
    def setUp(self):
        self.model=_phi3('dummy')
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
        lines=[x for x in self.g3.xInternalLines()]
        sub=subgraphs.Subgraph(lines[0:2])
        assert sub.Dim(self.model)==-4

class test_subgraphs:
    def setUp(self):
        self.g=Graph('e12-e3-33-')
        self.model=_phi3('dummy')
        self.model.SetTypes(self.g)
        self.phi4=_phi4('dummy')

    

    def test_FindSubgraphs(self):
        def findsubgraphs(nickel,model):
            g=Graph(nickel)
            model.SetTypes(g)
            res=[]
            for sub in subgraphs.FindSubgraphs(g,model):
                g1=Graph(sub.ToEdges())
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
                        return subgraphs.Subgraph((line,reverse[out_nodes[line]]))
    
#     def test_FindExternal(self):
#         nodes,lines= subgraphs.FindExternal(self.findsub(self.g))
#         print self.findsub(self.g)
#         print [x.idx() for x in nodes], lines
#         print self.g._edges()
# 
#         assert False

    def test_ToEdges(self):
        print self.findsub(self.g) , self.g._lines
        print self.findsub(self.g).ToEdges()
        g1=Graph(self.findsub(self.g).ToEdges())
        g1.GenerateNickel()
        assert str(g1.nickel)=='e11-e-'

