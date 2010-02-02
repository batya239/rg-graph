#!/usr/bin/python
# -*- coding:utf8

#import sympy

class Model:
    """ Class represents necessary information about model
        LineTypes - dict of line types (for now - 1 record)
        NodeTypes - dict of vertex types
        subgraphs - list of lists of LineTypes?
    """
    def __init__(self,name):
        self.Name=name
        self.vLineTypes=dict()
        self.vNodeTypes=dict()
    def addLineType(self,LineIdx,**kwargs):
        """ propagator,directed
            propagator="1/(p*p+tau)", directed=0 (simple massive line)
            only for static!!! для динамики нужно оперировать полями
        """
        self.vLineTypes[LineIdx]=kwargs
    def addNodeType(self,NodeIdx,**kwargs):
        """ Lines(types),Factor
            Lines=[1,1,1], Factor=1 (simple phi3 vertex)
            Lines=[1,1], Factor=p1*p1 ( phi2 vertex with p^2 in it )
            Lines=[], Factor=1 (External node?)

        """
        self.vNodeTypes[NodeIdx]=kwargs
    def __str__(self):
        res="Model Name = %s\n\nLine types:\n" %self.Name
        for idxL in self.vLineTypes:
            res=res+"\ttype %s : %s\n" %(idxL,self.vLineTypes[idxL])
        res=res+" \nNode types:\n"
        for idxN in self.vNodeTypes:
            res=res+"\ttype %s : %s\n" %(idxN,self.vNodeTypes[idxN])
        return res
        
