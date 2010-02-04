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
        self.LineTypes=dict()
        self.NodeTypes=dict()
    def addLineType(self,LineIdx,**kwargs):
        """ propagator,directed,Graphviz
            propagator="1/(p*p+tau)", directed=0 (simple massive line)
            only for static!!! для динамики нужно оперировать полями
            Graphviz - additional options for vizualization, Ex. color="red"
        """
        self.LineTypes[LineIdx]=kwargs
    def addNodeType(self,NodeIdx,**kwargs):
        """ Lines(types),Factor, graphviz
            Lines=[1,1,1], Factor=1 (simple phi3 vertex)
            Lines=[1,1], Factor=p1*p1 ( phi2 vertex with p^2 in it )
            Lines=[], Factor=1 (External node?)
            Graphviz - additional options for vizualization, Ex. color="red"

        """
        self.NodeTypes[NodeIdx]=kwargs
    def __str__(self):
        res="Model Name = %s\n\nLine types:\n" %self.Name
        for idxL in self.LineTypes:
            res=res+"\ttype %s : %s\n" %(idxL,self.LineTypes[idxL])
        res=res+" \nNode types:\n"
        for idxN in self.NodeTypes:
            res=res+"\ttype %s : %s\n" %(idxN,self.NodeTypes[idxN])
        return res
        
