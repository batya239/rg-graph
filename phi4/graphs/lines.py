#!/usr/bin/python
# -*- coding:utf8
from store import _Nodes
class Line:
    """ Class represents lines
        type=, momenta=, start=, end=, modifiers=
    """
    def __init__(self,type=None, momenta=None, modifiers=None, **kwargs):
        required_fields = set(['start','end'])
        if not required_fields.issubset(set(kwargs.keys())):
             raise ValueError, "Lines required fields are %s"%required_fields
        self.type=type
        self.momenta=momenta
        self.modifiers=modifiers
        for field in kwargs:
            self.__dict__[field] = kwargs[field]

    def Nodes(self):
        if not "_nodes" in self.__dict__:
            _nodes_store=_Nodes()
            self._nodes=(_nodes_store.Get(self.start), _nodes_store.Get(self.end))
        return self._nodes
        

    def Propagator(self, model):
        """ line propagator
        """
        return model.propagator(self)

    def Dim(self, model):
        """ line dimension
        """
        return model.Dim(self)

    def idx(self):
        return self._store_idx

    def isInternal(self):
#        print self.idx(), self.Nodes()[0].isInternal,  self.Nodes()[1].isInternal
        return self.Nodes()[0].isInternal() and self.Nodes()[1].isInternal()
    
    def __repr__(self):
        return "%s:[%s,%s]"%(self.idx(),self.start,self.end)

