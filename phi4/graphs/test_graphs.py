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
        g=Graph("e11-e-")
        print g._lines, g._nodes
        assert ((g._lines==self.e11_e_lines) and 
                (g._nodes==self.e11_e_nodes))

    def test_init_list(self):
        """ creating graph from adjacency list
        """
        g=Graph([[-1,0],[0,1],[0,1],[-1,1]])
        print g._lines, g._nodes
        assert ((g._lines==self.e11_e_lines) and 
                (g._nodes==self.e11_e_nodes))

    def test_edges(self):
        """ check that created graph has correct adjacency list
        """
        a=[[-1,0],[0,1],[0,1],[-1,1]]
        print  Graph(a).edges(), sorted_list(a)
        assert Graph(a).edges()==sorted_list(a)
        print  Graph('e11-e-').edges(), sorted_list(a)
        assert Graph('e11-e-').edges()==sorted_list(a)
        a=[[-1,0],[0,1],[0,1],[0,1],[-1,1]]
        assert Graph(a).edges()==sorted_list(a)
        assert Graph('e111-e-').edges()==sorted_list(a)
