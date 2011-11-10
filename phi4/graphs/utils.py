#!/usr/bin/python
# -*- coding: utf8

import time                                                
import re as regex
import sympy
import copy
from graphs import Graph

def S(d):
    return d*sympy.pi**(d/2.)/sympy.special.gamma_functions.gamma(d/2.+1)

def det(matrix):
    _matrix=matrix.clone()
    var_lst=[]
    for i in range(_matrix.shape[0]):
        for j in range(_matrix.shape[1]):
            if matrix[i, j]<>0:
                var=sympy.var('matr_%s_%s'%(i, j))
                _matrix[i, j]=var
                var_lst.append((var, (i, j)))
    det1=_matrix.det()
    for item in var_lst:
        (var, (i, j) )=item
        det1=det1.subs(var, matrix[i, j])
        
    return det1.expand()
    
    

def series_lst(expr, var, n):
    """ f_0+var*f_1+...+var^n*f_n
    """
    if n<0:
        raise ValueError,  "n = %s <0"%n
    res=[]
    if isinstance(expr,(float,int)):
        t_expr=sympy.Number(expr)
    else:
        t_expr=expr
    for i in range(n+1):
        res.append(t_expr.subs(var,0))
        t_expr=t_expr.diff(var)/(i+1)
    return res

def series_f(expr,var, n):
    res=0.
    idx=0
    for expr in series_lst(expr,var,n):
        res=res+expr.evalf()*var**(idx)
        idx+=1
    return res

    


def norm(n,d):
    if n>0:
        res = 1.
    if n>1:
        res = res*S(d-1)/S(d)
    if n>2:
        res = res*S(d-2)/S(d)
    if n>3:
        res = res*S(d-3)/S(d)
    if n>4:
        raise NotImplementedError, "not implemented n=%s, d=%s"%(n,d)
    return res



def LoadFromGRC(filename, model):

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
    
    res = dict()
    lines = open(filename,"r").read().splitlines()
    node_types=dict()
    ext_nodes=SearchGRCExternalNodes(lines)
    for ext_node in ext_nodes:
        node_types[ext_node] = 0       
#    print ext_nodes
    
    for graph_lines in SplitGRCGraphs(lines):
        edges=[]
#        print graph_lines
        for line in graph_lines.values():
            newline=list()
            for node in line:
                if node in ext_nodes:
                    newline.append(-1)
                else:
                    newline.append(node)
            edges.append(newline)
#        print edges
        g=Graph(edges)
        if not tadpole(g,model):
            res[str(g.GenerateNickel())]=1
#         graph = Graph(model)
#         for idxL in graph_lines.keys():
#             graph.AddLine(idxL, 
#                           Line(model, 1, start=graph_lines[idxL][0], 
#                                end=graph_lines[idxL][1], 
#                                momenta=None, dots=dict()) 
#                           )
#             
#         graph.DefineNodes(node_types)
#         res.append(graph)
    return res.keys()

def tadpole(g,model):
    res=False
    model.SetTypes(g)
    g.FindSubgraphs(model)
    for sub in g._subgraphs+[g.asSubgraph()]:
        if sub.CountExtLegs()==2:
            if len(sub.BorderNodes())<>2:
                res=True
    return res






class TimerStorage:
    def __init__(self):
        self._count=dict()
        self._time=dict()
        self.store=True

    def Add(self, name, time):
        if name in self._count.keys():
            self._count[name]+=1
            self._time[name]+=time
        else:
            self._count[name]=1
            self._time[name]=time
    def Print(self):
	print "\n\nTiming statistics:"
        for name in self._count.keys():
            print "%s : %s / %s = %s"%(name,self._time[name],self._count[name],self._time[name]/float(self._count[name]))
	print "---------------------"



# Storage for Nodes of all graphs
class Timer( object ):
    ## Stores the unique Singleton instance-
    _iInstance = None
 
    ## Class used with this Python singleton design pattern
 
    ## The constructor
    #  @param self The object pointer.
    def __init__( self ):
        # Check whether we already have an instance
        if Timer._iInstance is None:
            # Create and remember instanc
            Timer._iInstance = TimerStorage()
 
        # Store instance reference as the only member in the handle
        self._EventHandler_instance = Timer._iInstance
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @return Attribute
    def __getattr__(self, aAttr):
        return getattr(self._iInstance, aAttr)
 
 
    ## Delegate access to implementation.
    #  @param self The object pointer.
    #  @param attr Attribute wanted.
    #  @param value Vaule to be set.
    #  @return Result of operation.
    def __setattr__(self, aAttr, aValue):
        return setattr(self._iInstance, aAttr, aValue)


def timeit(method):

    def timed(*args, **kw):
	
	timer=Timer()
	if timer.store:
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()
            timer.Add(method.__name__,te-ts)
        else:
            result = method(*args, **kw)

        return result

    return timed

def normalize_variable_name(var, symbol):
    """ for C_a5_a0_a2 normalized var name is C_a0_a2_a5
        indices are sorted in alphabetical order
    """
    s_var=str(var)
    s_symbol=str(symbol)
    t_list=s_var.split("_")
    ind_list=t_list[1:]
    ind_list.append(s_symbol)
    ind_list.sort()
    if len(ind_list)==1:
        res=t_list[0]+"_%s"%ind_list[0]
    else:
        res=t_list[0]+"_%s"%reduce(lambda x, y:"%s_%s"%(x, y),  ind_list)
    return sympy.var(res)
    
    

def diff(expr, symbol, exclude=list()):
    """ Perform differentiation of sympy expression expr by sympy variable symbol.
        exclude - list of patterns (regex) of symbols that does not depend on symbol. (i.e. diff(..)=0 )
    """
    
    if isinstance(expr, sympy.Mul):
        res=0.
        for arg in expr.args:
            res_=diff(arg,symbol,exclude=exclude)
            for arg2 in expr.args:
                if arg<>arg2:
                    res_=res_*arg2
            res+=res_
        return res
    elif isinstance(expr, sympy.Pow):
        a,b=expr.args
        return a**b*(diff(b,symbol,exclude=exclude)*sympy.log(a)+diff(a,symbol,exclude=exclude)*b/a)

    elif isinstance(expr, sympy.Add):
        res=0.
        for arg in expr.args:
            res+=diff(arg,symbol,exclude=exclude)
        return res
    elif isinstance(expr,sympy.Symbol):
        if expr == symbol:
            return sympy.Number(1)
        elif ([regex.match(i,str(expr))<>None for i in exclude]).count(True)==0:
            return normalize_variable_name(expr,symbol)
        else:
            return 0
    elif isinstance(expr,sympy.Number):
        return 0
    else:
        raise TypeError, "type: %s, %s"%(type(expr),expr)

