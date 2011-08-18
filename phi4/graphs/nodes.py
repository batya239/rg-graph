#!/usr/bin/p3ython
# -*- coding:utf8

from store import _Lines, _Nodes
from lines import Line

class Node:
    """ Class represens nodes
        type=, lines_dict=,
    """
    def __init__(self, type=None, modifiers=None, **kwargs):
        #required_fields = set(['lines'])
        required_fields = set()
        if not required_fields.issubset(set(kwargs.keys())):
            raise ValueError, "Nodes required fields are %s"%required_fields
        self.type=type
        self.modifiers=modifiers
        self.lines=list()
        for field in kwargs:
            self.__dict__[field] = kwargs[field]

    def Lines(self):
        if not "_lines" in self.__dict__:
            _lines_store=_Lines()
            self._lines=tuple([_lines_store.Get(x) for x in self.lines])
        return self._lines

    def AddLine(self, node_idx,type=None,modifiers=None):
        _lines_store=_Lines()
        _nodes_store = _Nodes()
        idx=_lines_store.Add(Line(type=type,modifiers=modifiers,start=self._store_idx,end=node_idx))
        # add line to current (start) node
        self.lines.append(idx)
        # add line to end node
        _nodes_store.Get(node_idx).lines.append(idx)
#TODO: change node type to None?
        return idx
 
    def RemoveLine(self,line_idx):
        _lines_store=_Lines()
        _nodes_store = _Nodes()
        for node in _line_store.Get(line_idx).Nodes():
            node.lines.remove(line_idx)
#TODO: change node type to None?
        _line_store.Remove(line_idx)

    def Vertex(self, model, graph):
        """ node vertex factor
        """
#TODO: implement vertex
        pass
    def Dim(self, model):
        return model.Dim(self)

    def idx(self):
        return self._store_idx

    def isInternal(self):
        return (self.type == None) or (self.type>0)

    def OutNodes(self):
        """ returns dict: keys - lines, values - node connected by this line
        """
        out_nodes=dict()
        for line in self.Lines():
            for node in line.Nodes():
                if node<>self : 
                    out_nodes[line]=node.idx()
        return out_nodes

    def __repr__(self):
        return "Node-%s"%self.idx()


