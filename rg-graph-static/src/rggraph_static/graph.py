#!/usr/bin/python
# -*- coding: utf8

import nickel
import re as regex
from sympy import *

class Momenta:
    def __init__(self,**kwargs):
        def str2dict(string):
            if len(string) == 0:
                return dict()
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
            self.string = kwargs["string"].replace(" ","")
            self.dict = str2dict(self.string)
            for idxM in self.dict:
                var(idxM)
            if len(self.string) == 0:
                self.sympy = 0
            else:
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
            self.string=self.string.replace(" ","")
            if len(self.string) == 0:
                self.sympy = 0
            else:
                self.sympy = eval(self.string)

        elif "sympy" in kwargs:
            self.sympy = kwargs["sympy"]
            self.string = str(self.sympy).replace(" ","") 
            self.dict = str2dict(self.string)
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
    
    def __str__(self):
        return self.string
    
    def __abs__(self):
        return sqrt(self.Squared())
    
    def __mul__(self, other):
        if not isinstance(other,Momenta): 
            raise TypeError, "Cant multiply Momenta on non-Momenta %s" %other
        else:
            res = 0
            for atom1 in self.dict.keys():
                s_atom1=var(atom1)
                for atom2 in other.dict.keys():
                    s_atom2 = var(atom2)
                    if atom1 == atom2 :
                        res = res + self.dict[atom1]*other.dict[atom2]*s_atom1*s_atom2
                    elif atom1 > atom2 :
                        s_atom12 = var(atom2+"x"+atom1)
                        res = res + self.dict[atom1]*other.dict[atom2]*s_atom12
                    else:
                        s_atom12 = var(atom1+"x"+atom2)
                        res = res + self.dict[atom1]*other.dict[atom2]*s_atom12
        return res
    
    def Squared(self):
        return self*self
    
    def SetZeros(self, zero_momenta):
        t_sympy=self.sympy
        z_moment=list()
#        print t_sympy
        for idxZM in zero_momenta:
#            print "ZM : %s" %idxZM.string
            if len(idxZM.dict) == 1:
                if idxZM.string[0] == "-":
                    z_moment.append( (-idxZM.sympy, 0) )
                else:
                    z_moment.append( (idxZM.sympy, 0) )
            else:
                atoms_list = list(set(self.dict.keys()) & set(idxZM.dict.keys()))
                if len(atoms_list) > 0 :
                    t_left = atoms_list[0]
                    t_list=idxZM.dict.keys()
                    t_list.remove(t_left)
                    t_right=dict()
                    for idxM in t_list:
                        t_right[idxM]=idxZM.dict[idxM]/idxZM.dict[t_left]*(-1)
                    z_moment.append( (Momenta(string=t_left).sympy, Momenta(dict=t_right).sympy) )

# TODO: нужна ли сортировка?
        z_moment.sort()
#        print "SetZeros z_moment: ", z_moment
        if not( isinstance(t_sympy,int) or isinstance(t_sympy,float)):
            for idxZeq in z_moment:
                t_sympy=t_sympy.subs(idxZeq[0],idxZeq[1])

        return Momenta(sympy=t_sympy)

def Streching(expr, moment_atom, strech):
    try:
        atoms = expr.atoms()
    except AttributeError:
        return expr
    t_expr = expr
    if strech in atoms:
        raise Exception, " %s  internal variable of Diff function, it shouldn't present in expression %s" %(strech, expr)
    
    for atom in atoms:
        if ("%sx" %moment_atom in str(atom)) or ("x%s" %moment_atom in str(atom)) or ("%s" %moment_atom == str(atom) ):
            t_expr = t_expr.subs(atom, strech * atom)
            
    return t_expr

def ExpandScalarProdAsVectors(expr, moment_atom, moment):
    try:
        atoms = expr.atoms()
    except AttributeError:
        return expr
    t_expr = expr
    for atom in atoms:
        
        if "%sx" %moment_atom in str(atom):
            vectors = str(atom).split('x')
            t_expr = t_expr.subs(atom, moment*Momenta(string=vectors[1]))
                                 
        elif "x%s" %moment_atom in str(atom):
            vectors = str(atom).split('x')
            t_expr = t_expr.subs(atom, moment*Momenta(string=vectors[0]))
            
        elif "%s" %moment_atom == str(atom):
            t_expr = t_expr.subs(atom,sqrt(moment*moment))
            
    return t_expr
            

class Line:
    """ Class represents information about Line of a graph
        idx, type, momenta, start, end 
    """
    def __init__(self, type_, start_, end_, momenta_, dots_):
        self.type = int(type_)
        self.start = int(start_)
        self.end = int(end_)
        if isinstance(momenta_,str):
            self.momenta = Momenta(string=momenta_)
        elif momenta_ == "None":
            self.momenta = None
        else:
            self.momenta = momenta_
        if isinstance(dots_,str):
            self.dots = eval(dots_)
        else:
            self.dots = dots_
        
         
    def Nodes(self):
        return (self.start, self.end)
    
    def __str__(self):
        dict={}
        map(lambda k,v: dict.update({k: str(v)}),self.__dict__.keys(),self.__dict__.values())
        return str(dict)
    
     


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
#            print idxL
#            print moment[idxL]
            self.AddLine(idxL, Line(1, lines[idxL][0], lines[idxL][1], 
                                    Momenta(string=moment[idxL]), dict()))
        
    
    def DefineNodes(self, dict_node_type=dict(), **kwargs):
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
            
            TODO: dimension count should be rewriten, for now there is 
            additional kwargs["dim"] argument to force dims of dotted ctgraphs
            to be correct
                       
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
        
#TODO : we must determine dim by power counting  
        if "dim" in kwargs :
            self.dim = kwargs["dim"]

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
                Out = -1
            else:
                Out = self.lines[idxL].end
            edges.append([In, Out])
        self.nickel=nickel.Canonicalize(edges)
        # calculate sym coefficient:
# TODO: vacuum loops ! 
        import copy
        edges = copy.copy(nickel.Nickel(nickel=self.nickel.nickel).edges)
        unique_edges = dict()
        for idx in edges:
            idx.sort()
            if str(idx) in unique_edges:
                unique_edges[str(idx)] = unique_edges[str(idx)] +1
            else:
                unique_edges[str(idx)] = 1
        C=Factorial(len(self.external_lines))/self.nickel.num_symmetries
        for idxE in unique_edges:
            C = C / Factorial(unique_edges[idxE])
        self.sym_coeff = C
        
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

    def Clone(self, **kwargs):
        G=self
        if "zero_moments" in kwargs:
            zm = kwargs["zero_moments"]
        else:
            zm = []
        from copy import deepcopy
    # TODO: python 2.5 has buggy copy.deepcopy function    
        graph_copy = Graph(G.model)
    #    graph_copy.lines = deepcopy(G.lines)
        for idxL in G.lines :
            graph_copy.AddLine(idxL, Line(G.lines[idxL].type, G.lines[idxL].start, G.lines[idxL].end, G.lines[idxL].momenta.SetZeros(zm), deepcopy(G.lines[idxL].dots)))
        graph_copy.nodes = dict()
        graph_copy.subgraphs = list()
        graph_copy.DefineNodes(G.GetNodesTypes())
        graph_copy.FindSubgraphs()
        return graph_copy
    
    def _ToDict(self):
        res = dict()
        res['model'] = self.model.name
        lines = dict()
        map(lambda k,v: lines.update({k: str(v)}),self.lines.keys(),self.lines.values())
        res['lines'] = lines
        res['node_types'] = self.GetNodesTypes()
        
        return res
    
    def _FromDict(self,dict):
        if dict['model']<> self.model.name:
            raise ValueError, "different model names! %s and %s " %(dict['model'],self.model.name)
        for idxL in dict['lines']:
            line = eval(dict['lines'][idxL])
            self.AddLine(idxL, Line(line['type'],line['start'],line['end'],line['momenta'],line['dots']))
        self.DefineNodes(dict['node_types'])
    
    def Save(self, overwrite=False):
        self.model.SaveGraph(self,overwrite)

    def Load(self, str_nickel=""):
        self._FromDict(self.model.LoadGraph(str_nickel))
        
    def NLoops(self):
        return len(self.internal_lines)-len(self.internal_nodes)+1
        
    def _UpdateMoments(self, moments):
        for idxL in moments:
            self.lines[idxL].momenta = Momenta(string=moments[idxL])
    def SaveResults(self):
        self.model.SaveResults(self)

        

def LoadFromGRC(filename,model):

#search for External nodes
    def SearchGRCExternalNodes(lines):
        res = []
        for idx in range(len(lines)):
            reg = regex.match("External\s*=\s*(\d+);",lines[idx])
            if reg:
                n_external_lines = int(reg.groups()[0])
                break
            
        
        external_start = idx
        for idx in range(external_start+1,len(lines)):
            reg = regex.match("Eend;", lines[idx])

            if reg:
                break
            reg = regex.match("\s*(\d+)\s*=.*;$", lines[idx])
            if reg:
                res.append(int(reg.groups()[0]))
        return res
    
    def SplitGRCGraphs(lines):
        res = []
        graph = False
        for line in lines:
            reg = regex.match("Graph\s*=",line)
            if reg and (not graph):
                graph = True
                graph_lines = dict()
            reg = regex.match("Gend;",line)
            if reg and graph:
                graph = False
                res.append(graph_lines)
            if graph:
                reg1 = regex.match("\s*(\d+)=\{(.+)\};",line)
                if reg1:
#TODO: обрабатываются линии только одного типа!!!
                    cur_node=int(reg1.groups()[0])
                    str_lines = reg1.groups()[1].split(",")
                    for str_line in str_lines:
                        reg2 = regex.match("^\s*(\d+)\[.*\]$",str_line)
                        if reg2:
                            cur_line = int(reg2.groups()[0])
                        else:
                            raise ValueError, "error while parsing grc nodes: %s" %str_line
                        if cur_line in graph_lines.keys(): 
                            graph_lines[cur_line].append(cur_node)
                        else:
                            graph_lines[cur_line] = [cur_node,]
        return res
    
    res = list()
    lines = open(filename,"r").read().splitlines()
    node_types=dict()
    for ext_node in SearchGRCExternalNodes(lines):
        node_types[ext_node] = 0       
    
    for graph_lines in SplitGRCGraphs(lines):
        graph = Graph(model)
        for idxL in graph_lines.keys():
            graph.AddLine(idxL, Line(1,graph_lines[idxL][0],graph_lines[idxL][1],None,dict()) )
        graph.DefineNodes(node_types)
        res.append(graph)
    return res


