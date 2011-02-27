#!/usr/bin/python
# -*- coding:utf8

class Node:
    """ Class represens nodes
        type=, lines_dict=,
    """
    def __init__(self,**kwargs):
        required_fields = set(['type','lines_dict','modifiers'])
        if not required_fields.issubset(set(kwargs.keys())):
            raise ValueError, "Nodes required fields are %s"%required_fields
        for field in kwargs:
            self.__dict__[field] = kwargs[field]

    def Lines(self):
        return self.lines_dict.keys()


