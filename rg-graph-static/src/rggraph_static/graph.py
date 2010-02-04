#!/usr/bin/python
# -*- coding: utf8

from model import Model

class Line:
    """ Class represents information about Line of a graph
        idx, type, Momenta, In, Out 
    """
    def __init__(self, Ltype, LIn, LOut, LMomenta):
         self.Type = Ltype
         self.In = LIn
         self.Out = LOut
         self.Momenta = LMomenta
         
    def Nodes(self):
         return (self.In, self.Out)
     


class Node:
     """ Class represents information about Node of a graph
          idx, type, Lines
#### ??          getFactor()
     """
     def __init__(self, **kwargs):
          """  в кваргз можно было бы указать например что вершина продифференцированна или тип вершины.
          """
          self.Lines=tuple(kwargs["Lines"])
          self.Type=kwargs["Type"]



class Graph:
     """ Class represents information about graph
         Lines - dict of Line objects
         Nodes - dict of Node objects
             adjList
         subgraphs - list of Graph objects
     """
     def __init__(self, vModel):
          self.Lines = dict()
          self.Nodes = dict()
          self.adjList = dict()
          self.subgraphs = list()
          self.model = vModel
        
     def addLine(self, idx, Line):
          self.Lines[idx] = Line
          
     def LoadLinesfromFile(self,filename):
# подразумевается что пока что линии одного типа!! для линий разного типа должен быть другой формат файла
 
         (moment,Lines)=eval(open("moment").read())
         for idxL in Lines:
            tmpLine=Line(1,Lines[idxL][0],Lines[idxL][1],moment[idxL])
            self.addLine(idxL,tmpLine)
        
    
     def defineNodes(self, dictNodeType):
                               
           tmpNodeLines = dict()
# пробегаем по всем линиям для каждой вершины строим множество линий входящих/исходящих в нее
# вместе с типами этих линий  (для определения типа вершины)         
           for idxL in self.Lines:
               for idxN in self.Lines[idxL].Nodes():
                   if idxN in tmpNodeLines:
                       tmpNodeLines[idxN] = tmpNodeLines[idxN] | set([(idxL,self.Lines[idxL].Type),])
                   else:
                       tmpNodeLines[idxN] = set([(idxL,self.Lines[idxL].Type),])
                          

           for idxN in tmpNodeLines:
               # определяем тип вершины.
               (tmpLines,tmpLineTypes) = zip(*tmpNodeLines[idxN])
               tmplstLineTypes=list(tmpLineTypes)
               tmplstLineTypes.sort()
               if idxN in dictNodeType:
                   tmpType = dictNodeType[idxN]
                   if tmpType <> 0:
                       tmpNodeTypes=list(self.model.NodeTypes[idxT]["Lines"])
                       tmpNodeTypes.sort()
                       if tmpNodeTypes == tmplstLineTypes:
                           raise Exception, "invalid node type in dictNodeType"
               else:
                   tmpType = -1
                   for idxT in self.model.NodeTypes:
                       tmpNodeTypes=list(self.model.NodeTypes[idxT]["Lines"])
                       tmpNodeTypes.sort()
                       if tmpNodeTypes == tmplstLineTypes:
                           tmpType = idxT
                           break
                   if tmpType < 0: raise "no such node in model (node=%s)" %idxN
                   
               self.Nodes[idxN]=Node(Type=tmpType,Lines=tmpLines)               