#!/usr/bin/p3ython
# -*- coding:utf8

from lines import Line

class Node:
    """ Class represens nodes
        type=, lines_dict=,
    """
    def __init__(self, type=None, modifiers=list(), **kwargs):
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
       return tuple(self.lines)

    def AddLine(self, node, type=None, modifiers=list()):
       # add line to current (start) node
        line=Line(type=type,modifiers=modifiers,start=self,end=node)
        self.lines.append(line)
        # add line to end node
        node.lines.append(line)
#TODO: change node type to None?
        return line
 
#    def RemoveLine(self, line):
#        for node in line.Nodes():
#            node.lines.remove(line_idx)
##TODO: change node type to None?

    def Vertex(self, model):
        """ node vertex factor
        """
        return model.vertex(self)

    def Dim(self, model):
        return model.Dim(self)

    def idx(self):
        return self._idx

    def isInternal(self):
        return (self.type == None) or (self.type>0)

    def OutNodes(self):
        """ returns dict: keys - lines, values - node connected by this line
        """
        out_nodes=dict()
        for line in self.Lines():
            for node in line.Nodes():
                if node<>self : 
                    out_nodes[line]=node
        return out_nodes

    def __repr__(self):
        if len(self.modifiers)==0:
            return "%s"%self.idx()
        else:
            return "%s%s"%(self.idx(),self.modifiers)

    def AddModifier(self,str_modifier):
        self.modifiers.append(str_modifier)

