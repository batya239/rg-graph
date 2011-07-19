#!/usr/bin/python
import copy
from nose.tools import raises
from graphs import _find_empty_idx, Graph

def sorted_list(list_):
    res=copy.copy(list_)
    res.sort()
    return res   


class Test_fns:
    def test_find_empty_idx(self):
        assert 0==_find_empty_idx([])
        assert 1==_find_empty_idx([0])
        assert 4==_find_empty_idx([0,1,2,3])
        assert 2==_find_empty_idx([0,1,3])
        assert 1==_find_empty_idx([3,2,0])
        assert 0==_find_empty_idx(["0"])
        assert 1==_find_empty_idx(["0",0])


class Test_Graph:
    def setUp(self):
        self.e11_e_lines={0:[-1,0], 1:[-1,1], 2:[0,1], 3:[0,1]}
        self.e11_e_nodes={-1:[0,1], 0:[0,2,3], 1:[1,2,3]}
    def test_init_str(self):
        """ creating graph from nickel string
        """
#TODO: rewrite
        g=Graph("e11-e-")
        print g._lines, g._nodes
        g.GenerateNickel()
        assert str(g.nickel)=='e11-e-'

    def test_init_list(self):
        """ creating graph from adjacency list
        """
#TODO: rewrite
        g=Graph([[-1,0],[0,1],[0,1],[-1,1]])
        print g._lines, g._nodes
        g.GenerateNickel()
        assert str(g.nickel)=='e11-e-'

#     def test_edges(self):
#         """ check that created graph has correct adjacency list
#         """
#         a=[[-1,0],[0,1],[0,1],[-1,1]]
#         print  Graph(a).edges(), sorted_list(a)
#         assert Graph(a).edges()==sorted_list(a)
#         print  Graph('e11-e-').edges(), sorted_list(a)
#         assert Graph('e11-e-').edges()==sorted_list(a)
#         a=[[-1,0],[0,1],[0,1],[0,1],[-1,1]]
#         assert Graph(a).edges()==sorted_list(a)
#         assert Graph('e111-e-').edges()==sorted_list(a)
# 
    def test_nickel(self):
        """ check that generated diagrams has correct  nickel index
        """
        a=[[-1,0],[0,1],[0,1],[-1,1]]
        g1=Graph(a)
        g1.GenerateNickel()
        print  "!%s!"%g1.nickel, 'e11-e-', g1.nickel=='e11-e-'
        assert str(g1.nickel)=='e11-e-'
        g2=Graph('e11-e-')
        g2.GenerateNickel()
        print  g2.nickel, 'e11-e-'
        assert str(g2.nickel)=='e11-e-'
#        a=[[-1,0],[0,1],[0,1],[0,1],[-1,1]]
  #      assert Graph(a).edges()==sorted_list(a)
        g3=Graph('e111-e-')
        g3.GenerateNickel()
        assert str(g3.nickel)=='e111-e-'

    def test_xInternalNodes(self):
        """ check iterator on internal nodes
        """
        def intnodescount(nickel):
            g=Graph(nickel)
            res=[]
            for node in g.xInternalNodes():
                res.append(node)
            return len(res)
        assert intnodescount('e11-e-')==2
        assert intnodescount('e111-e-')==2
        assert intnodescount('e12-e3-33-')==4
        assert intnodescount('e12-e2-e-')==3

    def test_xInternalLines(self):
        """ check iterator on internal lines
        """
        def intlinescount(nickel):
            g=Graph(nickel)
            res=[]
            for line in g.xInternalLines():
                res.append(line)
            print res
            return len(res)
        assert intlinescount('e11-e-')==2
        assert intlinescount('e111-e-')==3
        assert intlinescount('e12-e3-33-')==5
        assert intlinescount('e12-e2-e-')==3

    def test_nloops(self):
        assert Graph('e11-e-').NLoops()==1
        assert Graph('e111-e-').NLoops()==2
        assert Graph('e12-e3-33-').NLoops()==2
        assert Graph('e12-e2-e-').NLoops()==1