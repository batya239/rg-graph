#!/usr/bin/python
from nose.tools import raises
from graphs import _find_empty_idx, Graph

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
        self.e11_e_lines={0:[-1,0], 1:[0,1], 2:[0,1], 3:[-1,1]}
        self.e11_e_nodes={-1:[0,3], 0:[0,1,2], 1:[1,2,3]}
    def test_init_str(self):
        g=Graph("e11-e-")
        print g._lines, g._nodes
        assert ((g._lines==self.e11_e_lines) and 
                (g._nodes==self.e11_e_nodes))

    def test_init_list(self):
        g=Graph([[-1,0],[0,1],[0,1],[-1,1]])
        print g._lines, g._nodes
        assert ((g._lines==self.e11_e_lines) and 
                (g._nodes==self.e11_e_nodes))

    
