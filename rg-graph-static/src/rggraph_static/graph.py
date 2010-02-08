#!/usr/bin/python
# -*- coding: utf8

from model import Model
import nickel

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
#        self.adjList = dict()
        self.subgraphs = list()
        self.model = vModel
        self.InternalLines = set([])
        self.ExternalLines = set([])
        self.InternalNodes = set([]) # nodes with types >0
        self.Type=-1
        self.nickel=None
        
    def __str__(self):
        res="Model = %s , Type = %s \n Lines: {" %(self.model.Name, self.Type)
        for idxL in self.Lines:
            res=res+" %s: [%s, %s]," %(idxL,self.Lines[idxL].In,self.Lines[idxL].Out)
        res=res[:-1]+ "}\n"
        return res
        
    def AddLine(self, idx, Line):
        self.Lines[idx] = Line
          
         
          
    def LoadLinesFromFile(self,filename):
# подразумевается что пока что линии одного типа!! для линий разного типа должен быть другой формат файла
 
        (moment,Lines) = eval(open(filename).read())
        for idxL in Lines:
            self.AddLine(idxL,Line(1,Lines[idxL][0],Lines[idxL][1],moment[idxL]))
        
    
    def DefineNodes(self, dictNodeType):
        
        tmpIntNodes=set([])   
        tmpExternalLines = set([])                    
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
            tmplstLineTypes = list(tmpLineTypes)
            tmplstLineTypes.sort() # отсортированный список типов линий в текущей вершине
            if idxN in dictNodeType: # если эта вершина указана в словаре который подан на вход, то надо проверить правильный ли тип вершины. 
                tmpType = dictNodeType[idxN]
                if tmpType <> 0:
                    tmpNodeTypes = list(self.model.NodeTypes[tmpType]["Lines"])
                    tmpNodeTypes.sort()
                    if tmpNodeTypes <> tmplstLineTypes:
                        raise Exception, "invalid node type in dictNodeType model:%s Graph:%s" %(tmpNodeTypes,tmplstLineTypes)
            else:
                tmpType = -1
                for idxT in self.model.NodeTypes:
                    tmpNodeTypes = list(self.model.NodeTypes[idxT]["Lines"])
                    tmpNodeTypes.sort()
                    if tmpNodeTypes == tmplstLineTypes:
                        tmpType = idxT
                        break
                if tmpType < 0:
                    if len(tmplstLineTypes) == 1: #если в вершину входит всего одна линия - она определенно внешняя
                        tmpType = 0
                    else:
                        raise "no such node in model (node=%s , %s)" %(idxN,tmplstLineTypes) 
             
            if tmpType == 0: 
                tmpExternalLines = tmpExternalLines | set(tmpLines)
            else:
                tmpIntNodes = tmpIntNodes | set([idxN,])    
                 
            self.Nodes[idxN] = Node(Type = tmpType, Lines = tmpLines)
            
        self.ExternalLines=tmpExternalLines
        self.InternalLines=set(self.Lines.keys())-self.ExternalLines
        import subgraph
        self.Type=subgraph.FindSubgraphType(self, list(self.InternalLines), self.model.SubGraphTypes)
        self.InternalNodes=tmpIntNodes
    
    def GetNodesTypes(self):
        res=dict()
        for idxN in self.Nodes:
            res[idxN]=self.Nodes[idxN].Type
        return res
    
    def GenerateNickel(self):
        edges = []
        for idxL in self.Lines:
             if self.Nodes[self.Lines[idxL].In].Type == 0:
                 In = -1
             else:
                 In = self.Lines[idxL].In
             if self.Nodes[self.Lines[idxL].Out].Type == 0:
                 In = -1
             else:
                 Out = self.Lines[idxL].Out
             edges.append([In, Out])
        self.nickel=nickel.Canonicalize(edges)
        
    def FindSubgraphs(self,SubGraphTypes = False):
        import subgraph
        if SubGraphTypes == False:
            SubGraphTypes=self.model.SubGraphTypes
        self.subgraphs=subgraph.Find(self, SubGraphTypes)
         
    def SaveAsPNG(self, filename):
        from visualization import GraphSubgraph2dot
#        import pydot
        gdot=GraphSubgraph2dot(self)
        gdot.write_png(filename,prog="dot")
        
            