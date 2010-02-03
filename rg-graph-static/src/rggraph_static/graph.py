#!/usr/bin/python
# -*- coding: utf8

from model import Model

class Line:
    """ Class represents information about Line of a graph
        idx, type, Momenta, In, Out 
    """
    def __init__(self,Ltype,LIn, LOut, LMomenta):
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
     def __init__(self,G,**kwargs):
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
          self.Lines=dict()
          self.Nodes=dict()
          self.adjList=dict()
          self.subgraphs=list()
          self.model=vModel
        
     def addLine(self,Line):
          self.Lines[idx]=Line
        
    
     def defineNodes(self,dictNodeType):
          
           def NodeLines2Type(NodeLines):
               res=[]
                 
               for idx in NodeLines:
                   
                   res.append(NodeLines[1])
               return res
            
                     
           tmpNodeLines=dict()
# пробегаем по всем линиям для каждой вершины строим множество линий входящих/исходящих в нее
# вместе с типами этих линий  (для определения типа вершины)         
           for idxL in self.Lines:
               for idxN in self.Lines[idxL].Nodes():
                   if idxN in tmpNodesLines:
                       tmpNodeLines[idxN]=tmpNodeLines[idxN]|set([(idxL,self.Lines[idxL].Type),])
                   else:
                       tmpNodeLines[idxN]=set([(idxL,self.Lines[idxL].Type),])
                          
# определяем тип вершины.
           for idxN in tmpNodeLines:
               if idxN in dictNodeType:
                   tmpType=dictNodeType[idxN]
                   if tmpType<>0:
                       if self.model.NodeTypes[tmpType].sort() <> NodeLines2Type(tmpNodeLines[idxN]).sort(): 
                           raise Exception, "invalid node type in dictNodeType"
               else:
                   tmpType=-1
                   for idxT in self.model.NodeTypes:
                       if self.model.NodeTypes[idxT].sort() == NodeLines2Type(tmpNodeLines[idxN]).sort():
                           tmpType=idxT
                           break
                   if tmpType<0: raise "no such node in model (node=%s)" %idxN
               