#!/usr/bin/python
# -*- coding:utf8

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
        return (self.start, self.end)

    def Propagator(self, model):
        """ line propagator
        """
        return model.propagator(self)

    def Dim(self, model):
        """ line dimension
        """
        return model.dim(self)


