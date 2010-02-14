#!/usr/bin/python
# -*- coding: utf8

import nickel
from sympy import *

class Momenta:
    def __init__(self,**kwargs):
        def str2dict(string):
            t_string=string.replace("+",",+").replace("-",",-")
            if t_string[0] == ",":
                t_string = t_string[1:]
            t_list=t_string.split(",")
            t_dict={}
            for idxM in t_list:
                if "+" in idxM:
                    t_dict[idxM.replace("+","")]=1
                elif "-" in idxM:
                    t_dict[idxM.replace("-","")]=-1
                else:
                    t_dict[idxM]=1
            return t_dict
            
        if "string" in kwargs:
            self.string = kwargs["string"]
            self.dict = str2dict(self.string)
            for idxM in self.dict:
                var(idxM)
            self.sympy = eval(self.string)
            
        elif "dict" in kwargs:
            self.dict = kwargs["dict"]
            self.string = ""
            for idxM in self.dict:
                var(idxM)
                if self.dict[idxM] == 1 :
                    self.string = "%s+%s" %(self.string, idxM)
                elif self.dict[idxM] == -1 :
                    self.string = "%s-%s" %(self.string, idxM)
                else:
                    raise ValueError, "invalid momenta %s" %self.dict
            self.sympy = eval(self.string)
        elif "sympy" in kwargs:
            self.sympy = kwargs[sympy]
            self.string = str(self.sympy) 
            self.dict = str2dict(self.sympy)
        else:
            raise TypeError, "unknown moment datatype kwargs = %s" %kwargs
         
    def __neg__(self):
        t_dict=dict()
        for idxD in self.dict:
            t_dict[idxD] = - self.dict[idxD]
        return Momenta(dict=t_dict) 
    
    def __add__(self, other):
        return Momenta(sympy=self.sympy+other.sympy)
    
    def __sub__(self, other):
        return Momenta(sympy=self.sympy+other.sympy)
    
    def Squared(self):
        res = 0
        for idxM in self.dict:
            var(idxM)
        t_list=self.dict.keys()
        t_list.sort()
        for idxM in t_list:            
            res=res+eval(idxM)*eval(idxM)
            for idxM2 in t_list[t_list.index(idxM)+1:]:
                var(idxM+idxM2)
                res = res + 2 * self.dict[idxM] * eval(idxM) * self.dict[idxM2] * eval(idxM2) * eval(idxM+idxM2)
        return res
    
    def SetZeros(self, zero_momenta):
        t_sympy=self.sympy
        z_moment=list()

        for idxZM in zero_momenta:
            if len(idxZM) == 1:
                z_moment.append( (idxZM.sympy, 0) )
            else:
                t_list=idxZM.dict.keys()
                t_left=t_list[0]
                t_right=dict()
                for idxM in t_list[1:]:
                    t_right[idxM]=idxZM.dict[idxM]/idxZM.dict[t_left]*(-1)
                z_moment.append( (Momenta(string=t_left).sympy, Momenta(dict=t_right).sympy) )

        for idxZeq in z_moment:
            t_sympy=t_sympy.subs(idxZeq[0],idxZeq[1])

        return Momenta(sympy=t_sympy)
                    
                
            
    
    

class Line:
    """ Class represents information about Line of a graph
        idx, type, momenta, start, end 
    """
    def __init__(self, type_, start_, end_, momenta_, dots_):
        self.type = type_
        self.start = start_
        self.end = end_
        self.momenta = momenta_
        self.dots = dots_
        
         
    def Nodes(self):
        return (self.start, self.end)
    
     


class Node:
    """ Class represents information about Node of a graph
        type, Lines

    """
    def __init__(self, **kwargs):
        """  в кваргз можно было бы указать например что вершина продифференцированна или тип вершины.
        """
        self.lines=tuple(kwargs["Lines"])
        self.type=kwargs["Type"]



class Graph:
    """ Class represents information about graph
         lines - dict of Line objects
         nodes - dict of Node objects
         subgraphs - list of Graph objects
         model - Model object
         internal_lines - set of internal lines of the graph
         external_lines - set of external lines of the graph
         internal_nodes - set of internal nodes of the graph 
                          (nodes that have at least one internal line)
         type - type of the graph (as defined in model.subgraph_types)
         nickel - nickel object ( used for calculation unique index 
                                  of the graph) 
    """
    def __init__(self, model_):
        """ Initializes empty Graph instance. 
        """
        self.lines = dict()
        self.nodes = dict()
        self.subgraphs = list()
        self.model = model_
        self.internal_lines = set([])
        self.external_lines = set([])
        self.internal_nodes = set([]) # nodes with types >0
        self.type=-1
        self.nickel=None
        
    def __str__(self):
        """ Converts Graph to string representation for printing
            model, type and lines information printed
        """
        res="Model = %s , Type = %s \n Lines: {" %(self.model.name, self.type)
        for idxL in self.lines:
            res=res+" %s: [%s, %s]," %(idxL, self.lines[idxL].start, 
                                       self.lines[idxL].end)
        res=res[:-1]+ "}\n"
        return res
        
    def AddLine(self, idx, line):
        """ add lines to empty subgraph
        
            TODO: avoid adding lines to graph after self.DefineNodes() call  
        """
        self.lines[idx] = line
          
         
          
    def LoadLinesFromFile(self,filename):
        """ temporary function to load graph information from
             files with old format
             
             TODO: information should be taken from grc file or 
                   file with new format. 
        """
# подразумевается что пока что линии одного типа!! 
#для линий разного типа должен быть другой формат файла
 
        (moment,lines) = eval(open(filename).read())
        for idxL in lines:
            self.AddLine(idxL, Line(1, lines[idxL][0], lines[idxL][1], 
                                    Momenta(string=moment[idxL]), dict()))
        
    
    def DefineNodes(self, dict_node_type):
        """ after definition of lines of the graph we construct self.nodes dict.
            self.nodes includes information about lines in nodes and node types
            
            node types are searched first in dict_node_type, 
            then in self.model.node_types
            
            dict_node_type argument used to force some nodes to have type that 
            we need. Used to define external nodes of subgraph, to define type 
            of nodes after extraction of subgraph and for inheritance of node 
            types from one graph to another (ex. from graph to counterterm 
            subgraph.)
            
            TODO: avoid to run DefineNodes twice on graph.   
             
        """
        tmp_int_nodes=set([])   
        tmp_external_lines = set([])                    
        tmp_node_lines = dict()
# пробегаем по всем линиям для каждой вершины строим множество линий 
# входящих/исходящих в нее вместе с типами этих линий  (для определения 
# типа вершины)
         
        for idxL in self.lines:
            for idxN in self.lines[idxL].Nodes():
                if idxN in tmp_node_lines:
                    tmp_node_lines[idxN] = tmp_node_lines[idxN] | set([(idxL,self.lines[idxL].type),])
                else:
                    tmp_node_lines[idxN] = set([(idxL,self.lines[idxL].type),])
                         

        for idxN in tmp_node_lines:
            
            # определяем тип вершины.
            (tmp_lines, tmp_line_types) = zip(*tmp_node_lines[idxN])
            tmp_lst_line_types = list(tmp_line_types)
            tmp_lst_line_types.sort() 
# отсортированный список типов линий в текущей вершине

            if idxN in dict_node_type: 
# если эта вершина указана в словаре который подан на вход, то 
# надо проверить правильный ли тип вершины. 
                tmp_type = dict_node_type[idxN]
                if tmp_type <> 0:
                    tmp_node_types = list(self.model.node_types[tmp_type]["Lines"])
                    tmp_node_types.sort()
                    if tmp_node_types <> tmp_lst_line_types:
                        raise Exception, "invalid node type in dictNodeType model:%s Graph:%s" %(tmp_node_types, tmp_lst_line_types)
            else:
                tmp_type = -1
                
# иначем пробегаем по типам вершин в модели и ищем подходящую
#
                for idxT in self.model.node_types:
                    tmp_node_types = list(self.model.node_types[idxT]["Lines"])
                    tmp_node_types.sort()
                    if tmp_node_types == tmp_lst_line_types:
                        tmp_type = idxT
                        break
                if tmp_type < 0:
                    if len(tmp_lst_line_types) == 1: #если в вершину входит всего одна линия - она определенно внешняя
                        tmp_type = 0
                    else:
                        raise "no such node in model (node=%s , %s)" %(idxN,tmp_lst_line_types) 
# если вершина внешняя:             
            if tmp_type == 0: 
                tmp_external_lines = tmp_external_lines | set(tmp_lines)
            else:
                tmp_int_nodes = tmp_int_nodes | set([idxN,])    
                 
            self.nodes[idxN] = Node(Type=tmp_type, Lines=tmp_lines)
            
        self.external_lines = tmp_external_lines
        self.internal_lines = set(self.lines.keys()) - self.external_lines
        import subgraph
        (self.type, self.dim) = subgraph.FindSubgraphType(self, 
                                list(self.internal_lines), 
                                self.model.subgraph_types)
        self.internal_nodes=tmp_int_nodes
    
    def GetNodesTypes(self):
        """ returns dict of types of nodes
        """
        res=dict()
        for idxN in self.nodes:
            res[idxN]=self.nodes[idxN].type
        return res
    
    def GenerateNickel(self):
        edges = []
        for idxL in self.lines:
            if self.nodes[self.lines[idxL].start].type == 0:
                In = -1
            else:
                In = self.lines[idxL].start
            if self.nodes[self.lines[idxL].end].type == 0:
                In = -1
            else:
                Out = self.lines[idxL].end
            edges.append([In, Out])
        self.nickel=nickel.Canonicalize(edges)
        
    def FindSubgraphs(self, subgraph_types = False):
        """ Finds subgraphs and put them in to self.subgraphs list
            if subgraph_types defined searches for subgraphs of custom type 
            not defined in self.model.subgraph_types  
        """
        import subgraph
        if subgraph_types == False:
            subgraph_types=self.model.subgraph_types
        self.subgraphs=subgraph.Find(self, subgraph_types)
         
    def SaveAsPNG(self, filename):
        """ saves graph and its subgraphs as png image
        """
        from visualization import GraphSubgraph2dot
#        import pydot
        gdot=GraphSubgraph2dot(self)
        gdot.write_png(filename, prog="dot")
        
#    def LinePropagator(self, idxL, zero_moments=[]):
#        cur_line = self.lines[idxL]
#        cur_momenta = cur_line.momenta.SetZeros(zero_moments)
#        propagator = self.model.line_types[cur_line.type]["propagator"](momenta=cur_momenta)
#        for idxD in cur_line.dots:
#            for idx in range(cur_line.dots[idxD]):
#                propagator = cur_line[idxD]["action"](propagator=propagator)
#        return propagator
#    
#    def NodeFactor(self, idxN, zero_moments=[]):
##TODO:  в реальности работает только со скалярными вершинами и врешинами в которые входит ровно один тип линий.         
#        cur_node = self.nodes[idxN]
#        moments = dict()
#        cnt_moment = 0
#        for idxL in cur_node.lines:
#            cur_line = cur_node.lines[idxL]
#            if cur_line.snd == idxN :
#                moment["momenta%s"%cnt_moment] = cur_line.momenta.SetZeros(zero_moments)
#            else:
#                moment["momenta%s"%cnt_moment] = - cur_line.momenta.SetZeros(zero_moments)
#            cnt_moment = cnt_mode + 1
#        factor = self.model.node_types[cur_node.type]["Factor"](graph=self, **moment)
#        return 
             
            