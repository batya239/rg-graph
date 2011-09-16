#!/usr/bin/python
# -*- coding:utf8

import copy
import sympy    

import nickel

from nodes import Node
from subgraphs import FindSubgraphs,Subgraph
#from lines import Line



def _find_empty_idx(keys_):
   idx=0
   while idx in keys_:
       idx+=1
   return idx


class Graph:
    def __init__(self,arg):
        self._lines = list()
        self._nodes = list()
        if isinstance(arg,str):
# construct graph from nickel index
            self._from_lines_list(nickel.Nickel(string=arg).edges)
        elif isinstance(arg,list):
# construct graph from edges 
            self._from_lines_list(arg)
        else:
            raise TypeError, "Unsupproted type of argument: %s"%arg

    def _Node(self,idx):
        return self._nodes[idx]

    def _Line(self,idx):
        return self._lines[idx]

    def _from_lines_list(self,list_):
        _lines_dict=dict()
        _nodes_dict=dict()
        list__=copy.copy(list_)
        list__.sort()
        for line in list__:
            if len(line) == 2:
                for node_idx in line[0:2]:
                    if node_idx not in _nodes_dict.keys():
                        _type=None
                        if node_idx<0:
                            _type=-1 #external node
                        _nodes_dict[node_idx]=Node(type=_type)
                self._lines.append(_nodes_dict[line[0]].AddLine(_nodes_dict[line[1]]))
                 
            else:
                raise ValueError, "Invalid line %s"%line
        self._nodes=_nodes_dict.values()
        self._reindex()

    def _reindex(self):
        for node_idx in range(len(self._nodes)):
            self._nodes[node_idx]._idx=node_idx
        for line_idx in range(len(self._lines)):
            self._lines[line_idx]._idx=line_idx
            
    def _edges(self):
        res=[]
        for line in self._lines:
            _nodes=[]
            for node in line.Nodes():
                if (node.type<>None) and (node.type<0) :
                    _nodes.append(-1)
                else:
                    _nodes.append(node.idx())
            res.append(_nodes)
#        res.sort()
        return res
                         
    def GenerateNickel(self):
        if 'nickel' not in self.__dict__:
            self.nickel=nickel.Canonicalize(self._edges())
        return self.nickel

    def xInternalNodes(self):
        
        for node in self._nodes:
            if node.isInternal():
                yield node

    def asSubgraph(self):
        if "_asSubgraph" not in self.__dict__:
            self._asSubgraph=Subgraph([x for x in self.xInternalLines()])
        return self._asSubgraph

    def xInternalLines(self):
        
        for line in self._lines:
            if line.isInternal():
                yield line

    def Lines(self):
        return self._lines
            

    def NLoops(self):
#TODO: rewrite nloops in more efficient way
        if "_nloops" not in self.__dict__:
            self._nloops = len([x for x in self.xInternalLines()])-len([x for x in self.xInternalNodes()])+1
        return self._nloops

    def Dim(self, model):

        dim = self.NLoops()*model.space_dim

        for line in self.xInternalLines():
            dim = dim + line.Dim(model)

        for node in self.xInternalNodes():
            dim = dim + node.Dim(model)

        return dim

    def FindSubgraphs(self,model):
        self._subgraphs=FindSubgraphs(self,model)

    def FindTadpoles(self):
        #subgraphs=[self.asSubgraph()] + sorted(self._subgraphs,key=len,revers=True)
        for sub in self._subgraphs+[self.asSubgraph()]:
            sub.FindTadpoles(self._subgraphs)

    def __str__(self):
        res=dict()
        for line in self._lines:
            res[line.idx()]=line.__repr__()
        return str(res)

    def Clone(self):
        return copy.deepcopy(self)

    def _moments(self):
        return dict([(x,x.momenta) for x in self._lines])

    def expr(self,model):
        res=sympy.Number(1)
        for node in self.xInternalNodes():
            res=res*node.Vertex(model)
        for line in self.xInternalLines():
            res=res*line.Propagator(model)
        
        d=sympy.var('d')
#         for i in range(self.NLoops()):
#             res=res*sympy.var('q%s'%i)**(d-1)
        return res

    def RemoveSubgaphs(self, sub_list):
        if "_subgraphs_m" in self.__dict__:
            raise Exception, "_subgraphs_m defined in graph"
        for sub in sub_list:
            self._subgraphs.remove(sub)

    def Clean(self, items = ['_subgraphs_m', '_nloops', '_asSubgraph','nickel','_subgraphs']):
        """ clean all cached values
        """
        for item in items:
            try:
                del self.__dict__[item]
            except:
                pass
    def RemoveLine(self, line):
        if line not in self._lines:
            raise ValueError, "line doesnt belongs to this graph"
        line.Nodes()[0].RemoveLine(line)
        self._lines.remove(line)
        
    def RemoveNode(self,node):
        if node not in self._nodes:
            raise ValueError, "node doesnt belongs to this graph"
        for line in node.Lines():
            self.RemoveLine(line)
        self._nodes.remove(node)

    def AddNode(self, node):
        if node in self._nodes:
            raise ValueError, "Node allready in graph"
        self._nodes.append(node)
#        print node
#        print self._nodes
        for line in node.Lines():
            if line not in self._lines:
                self.AddLine(line)
      

    def AddLine(self,line):
        if line in self._lines:
            raise ValueError, "Line allready in graph"
#        print self._nodes[3]       
        if line.Nodes()[0] not in self._nodes or line.Nodes()[1] not in self._nodes:
            raise ValueError, "One of nodes does not belong to graph nodes:%s, line: %s"%(self._nodes, line.Nodes())
        self._lines.append(line)
        self._reindex()        

    def ReduceSubgraphs(self, model):
        if not model.reduce:
            return self
        else:
            g=self.Clone()
            for sub in self._subgraphs:
#                print "'%s'"%sub.Nickel(), sub
                if str(sub.Nickel()) in model.subgraphs2reduce:
                    print "reducing: %s (%s)"%(sub.Nickel(), sub)
                    g=g.Clone()
                    newsub=g._subgraphs[self._subgraphs.index(sub)]
                    extnodes,extlines=newsub.FindExternal()
                    print newsub
                    nodes=list(newsub.BorderNodes())
                    if len(nodes)==2:
                        nodes2remove=set(newsub.InternalNodes())-newsub.BorderNodes()
                        for line in newsub._lines:
                            g.RemoveLine(line)

                        for node in nodes2remove:
                            g.RemoveNode(node)
                        

                        g.AddLine(nodes[0].AddLine(nodes[1], type=str(sub.Nickel())))

                    else:
                        raise Exception, "Can't  convert subgraph to line"
   
    
            g.Clean()
            return g
        