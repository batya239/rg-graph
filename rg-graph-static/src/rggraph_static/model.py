#!/usr/bin/python
# -*- coding:utf8

import utils
import graph
from sympy import *

class Model:
    """ Class represents necessary information about model
        LineTypes - dict of line types (for now - 1 record)
        NodeTypes - dict of vertex types
        subgraphs - list of lists of LineTypes?
    """
    def __init__(self, name_):
        self.name = name_
        self.line_types = dict()
        self.node_types = dict()
        self.subgraph_types = dict()
        self.k_nodetype_r1 = dict()
        self.dot_types = dict()
        self.greens=None
        
    def AddLineType(self, line_idx, **kwargs):
        """ propagator,directed,Graphviz
            propagator="1/(p*p+tau)", directed=0 (simple massive line)
            only for static!!! для динамики нужно оперировать полями
            Graphviz - additional options for vizualization, Ex. color="red"
        """
        if line_idx not in self.line_types:
            self.line_types[line_idx] = kwargs
        else:
            raise Exception, "LineType %s allready defined" %line_idx
        
    def AddNodeType(self, node_idx, **kwargs):
        """ Lines(types),Factor, graphviz
            Lines=[1,1,1], Factor=1 (simple phi3 vertex)
            Lines=[1,1], Factor=p1*p1 ( phi2 vertex with p^2 in it )
            Lines=[], Factor=1 (External node?)
            Graphviz - additional options for vizualization, Ex. color="red"

        """
        if node_idx not in self.node_types:
            self.node_types[node_idx] = kwargs
        else:
            raise Exception, "NodeType %s allready defined" %node_idx
    
    def AddSubGraphType(self, subgraph_idx, **kwargs):
        """ Lines(types), dim?? 
            K_nodetypeR1 - Maps  subgraph types to node types 
        """
        if subgraph_idx not in self.subgraph_types:
            self.subgraph_types[subgraph_idx] = kwargs
            if "K_nodetypeR1" in kwargs :
                self.k_nodetype_r1[subgraph_idx] = kwargs["K_nodetypeR1"]
        else:
            raise Exception, "SubGraphType %s allready defined" %subgraph_idx  

    def AddDotType(self, dot_idx, **kwargs):
        """ dim  
        """
        if dot_idx not in self.dot_types:
            self.dot_types[dot_idx] = kwargs
        else:
            raise Exception, "DotType %s allready defined,%s" %(dot_idx,self.dot_types)  

                
    def __str__(self):
        res = "Model Name = %s\n\nLine types:\n" %self.name
        for idxL in self.line_types:
            res = res + "\ttype %s : %s\n" %(idxL, self.line_types[idxL])
        res = res + " \nNode types:\n"
        for idxN in self.node_types:
            res = res + "\ttype %s : %s\n" %(idxN, self.node_types[idxN])
        res = res + " \nSubGraph types:\n"
        for idxS in self.subgraph_types:
            res = res + "\ttype %s : %s\n" %(idxS, self.subgraph_types[idxS])
        res = res + " \nDot types:\n"
        for idxD in self.dot_types:
            res = res + "\ttype %s : %s\n" %(idxD, self.dot_types[idxD])
        return res
    
    def GraphList(self):
        return self.GetGraphList(self)
    
    def GetGreens(self,reload=False, debug=False):
        if self.greens == None or reload:
            self.greens=dict()
            g_list = self.GraphList()
            g = var('g')
            for file in g_list:
                utils.print_debug("---: %s"%file, debug)
                G = graph.Graph(self)
                G.Load(str_nickel=file)
                G.DefineNodes({})
                G.GenerateNickel()
                G.LoadResults('eps')
                if len(G.green)>0 and G.green in self.greens and G.NLoops() <= self.target:
                    utils.print_debug("-----------------------: %s %s %s %s"%(G.green,G.sym_coeff, G.r1_gamma, g**G.NLoops()), debug)
                    self.greens[G.green] = self.greens[G.green] + G.sym_coeff * G.r1_gamma * g**G.NLoops()
                else:
                    self.greens[G.green] = G.sym_coeff * G.r1_gamma * g**G.NLoops() 
            for green in self.greens:
                self.greens[green]=utils.SimpleSeries(self.greens[green], g, 0, self.target)           
        else:
            return self.greens
    
    
#def scalar_prod(moment1, moment2):
#    if 'p' in moment1:
#        t_moment1 = moment1
#        t_moment2 = moment2
#    elif 'p' in moment2:
#        t_moment1 = moment2
#        t_moment2 = moment1
#    else:
#        n1 = int(moment1.replace("+q", "").replace("-q", ""))
#        n2 = int(moment2.replace("+q", "").replace("-q", ""))
#        if n1 < n2 :
#            t_moment1 = moment1
#            t_moment2 = moment2
#        else:
#            t_moment1 = moment2
#            t_moment2 = moment1
#    tt_moment1 = t_moment1.replace("+", "").replace("-", "")
#    tt_moment2 = t_moment2.replace("+", "").replace("-", "")
#    var(tt_moment1)
#    var(tt_moment2)
#    res  = 2*eval(t_moment1)*eval(t_moment2)
#    prod = tt_moment1 + tt_moment2
#    var(prod)
#    res = res * eval(prod)
#    return res
#
#def SquaredMomenta(momenta):
#    tmomenta = momenta.replace("+", ",+").replace("-", ",-")
#    moment_list = tmomenta[1:].split(',')
#    res=0
#    for idxM in moment_list:
#        var(idxM.replace('+','').replace('-',''))
#        res = res + pow(eval(idxM),2)
#        for idxM2 in moment_list[moment_list.index(idxM)+1:]:
#            res = res + scalar_prod(idxM,idxM2)
#    
#    return res
#
#def ZeroMomenta(momenta, zero_momenta):
#    tmomenta = momenta.replace("+", ",+").replace("-", ",-")
#    z_moment=list()
#    for idxZM in zero_momenta:
#        t_idxZM=idxZM.replace("+", ",+").replace("-", ",-")
#        idxZM_list=t_idxZM[1:].split()
#        if len(idxZM_list) == 1:
#            z_moment.append((idxZM_list[0].replace('+','').replace('-',''),'0'))
#        else:
#            if idxZM_list[0][0] == "-":
#                other = ""
#                for idxM in idxZM_list[1:]:
#                    other = other + idxM 
#                z_moment.append((idxZM_list[0].replace("-",""), other ))
#            else:
#                other = ""
#                for idxM in idxZM_list[1:]:
#                    other = other + idxM.replace('+','_+_').replace("-","_-_").replace("_+_","-").replace("_-_","+") 
#                z_moment.append((idxZM_list[0], other ))
#        tmomenta = tmomenta + idxZM.replace("+", ",+").replace("-", ",-")
#        
#    moment_list = tmomenta[1:].split(',')
#    res=0
#    for idxM in moment_list:
#        var(idxM.replace('+','').replace('-',''))
#    s_momenta=eval(momenta)    
#    for idxZM in z_moment:        
#        s_momenta=s_momenta.sub(eval(idxZM[0]),eval(idxZM[1]))
#    res=str(s_momenta)
#    if res[0] <> '-' :
#        res="+"+res
#    return res