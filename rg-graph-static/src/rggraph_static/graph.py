#!/usr/bin/python
# -*- coding: utf8

from model import Model

class Line:
    """ Class represents information about Line of a graph
        idx, type, Momenta, In, Out 
    """
    def __init__(self,Lidx,Ltype,LIn, LOut, LMomenta):
         self.Type=Ltype
         self.In=LIn
         self.Out=LOut
         self.Momenta=LMomenta
         
    def Nodes(self):
         return (self.In,self.Out)
     


class Node:
     """ Class represents information about Node of a graph
          idx, type, Lines
#### ??          getFactor()
     """
     def __init__(self,Nidx,G,**kwargs):
          """  в кваргз можно было бы указать например что вершина продиференцированна или тип вершины.
          """
          self.Lines=[]



class Graph:
     """ Class represents information about graph
         Lines - dict of Line objects
         Nodes - dict of Node objects
             adjList
         subgraphs - list of Graph objects
     """
     def __init__(self, vModel):
          self.vLines=dict()
          self.vNodes=dict()
          self.vadjList=dict()
          self.vsubgraphs=list()
          self.vmodel=vModel
        
     def addLine(self,Line):
          self.vLines[idx]=Line
        
    
     def defineNodes(self,dictNodeType):
           tmpNodeLines=dict()
# пробегаем по всем линиям для каждой вершины строим множество линий входящих/исходящих в нее
# вместе с типами этих линий  (для определения типа вершины)         
           for idxL in self.vLines:
                for idxN in idxL.Nodes():
                     if idxN in tmpNodes:
                          tmpNodeLines[idxN]=tmpNodeLines[idxN]|set([(idxL.idx,idxL.Type),])
                     else:
                          tmpNodeLines[idxN]=set([(idxL.idx,idxL.Type),])
                          

           for idxN in tmpNodeLines:
                if idxN in kwargs:
                     tmpType=kwargs[idxN]
                     if tmpType<>0:
                         if self.model.NodeTypes[tmpType].sort() <> tmpNodeLinesTypes[idxN].sort(): 
                             raise Exception, "invalid node type"
                else:
                     pass
