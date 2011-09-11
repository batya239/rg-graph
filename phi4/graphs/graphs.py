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
        self.nickel=nickel.Canonicalize(self._edges())

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
        for i in range(self.NLoops()):
            res=res*sympy.var('q%s'%i)**(d-1)
        return res

    def det(self,model):
        res=sympy.Number(1)
        d=sympy.var('d')
        for i in range(self.NLoops()):
            res=res*sympy.var('q%s'%i)**(d-1)
        if model.space_dim - self.NLoops()-2<0:
            raise ValueError, "Det not implemented: d=%s, nloops=%s "%(model.space_dim,self.NLoops())
        for i in range(self.NLoops()):
            for j in range(i+1,self.NLoops()):
                res=res*sympy.var('st_%s_%s'%(i,j))**(d-3-i)
        return res

    def subs_vars(self):
        res=dict()
        jakob=sympy.Number(1)
        for i in range(self.NLoops()):
            qi=sympy.var('q%s'%i)
            res['y%s'%i]=(1-qi)/qi
            jakob=jakob/qi/qi
            for j in range(i+1,self.NLoops()):
                ct_ij=sympy.var('ct_%s_%s'%(i,j))
                res['st_%s_%s'%(i,j)]=(1-ct_ij**2)**0.5
                res['ct_%s_%s'%(i,j)]=sympy.var('z_%s_%s'%(i,j))*2-1
                jakob=jakob*2

                if i == 0:
                    res['q%sOq%s'%(i,j)]=eval('ct_%s_%s'%(i,j))
                elif  i == 1:
                    res['q%sOq%s'%(i,j)]=eval('ct_0_{1}*ct_0_{2}+st_0_{1}*st_0_{2}*ct_{1}_{2}'.format(i,j))
                elif  i == 2:
                    res['q%sOq%s'%(i,j)]=eval('ct_0_{1}*ct_0_{2}+st_0_{1}*st_0_{2}*(ct_1_{1}*ct_1_{2}+st_1_{1}*st_1_{2}*ct_{1}_{2})'.format(i,j))
                else:
                    raise NotImplementedError, "nloops>4"
        return jakob, res
