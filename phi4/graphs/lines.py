#!/usr/bin/python
# -*- coding:utf8

class Line:
    """ Class represents lines
        type=, momenta=, start=, end=, dots=
    """
    def __init__(self,**kwargs):
        required_fields = set(['type','momenta','start','end','modifiers'])
        if not required_fields.issubset(set(kwargs.keys())):
             raise ValueError, "Lines required fields are %s"%required_fields
        for field in kwargs:
            self.__dict__[field] = kwargs[field]

    def Nodes(self):
        return (self.start, self.end)

    def Propagator(self, model):
        return model.propagator(self)

