#!/usr/bin/python
# -*- coding: utf8

'''
Created on Feb 20, 2010

@author: mkompan
'''
#Common generators


#from sympy import *
import sympy
import time
import sys

def xSelections(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for ss in xSelections(items, n-1):
                yield [items[i]]+ss

def xUniqueSelections(items, n):
    ''' Selections where [1,2] = [2,1]
    '''
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for ss in xUniqueSelections(items[i:], n-1):
                yield [items[i]]+ss

#def UniqueSelections(items,n):
#    lst = [i for i in xSelections(items,n)]
#    print lst
#    for idx in lst:
#        idx.sort()
#        print idx
#    print lst
#    return list(set(lst))

        

def xCombinations(seq, n):
    """Generator of all the n-element combinations of the given sequence.
    """
    if n == 0:
        yield seq[0:0]
    else:
        for i in range(len(seq)):
            for tail in xCombinations(seq[:i] + seq[i+1:], n - 1):
                yield seq[i:i+1] + tail


def xPermutations(seq):
    """Generator of all the permutations of the given sequence.
    """
    return xCombinations(seq, len(seq))

def xUniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xUniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc


def SimpleSeries(func,var,point,num):
# TODO: doesnt work sometimes.
    
    level=0
    flag=1
    if 'series' in dir(func):
        f=func.series(var,point=point,n=num+2)
    else:
        f=func
    try:    
        for OO in f.atoms(sympy.Order):
            f=f.subs(OO,0)
    except  AttributeError:
        pass
    res=0
    while(flag>0):
        tmp=sympy.limit(abs(f),var,point) 
        if type(tmp)==sympy.core.numbers.Infinity :
            level=level-1
            f=f*(var-point)
        else:
            if level<=num :
                res=sympy.limit(f,var,point)*pow(var-point,level)
            else:
                res=0
            flag=0

    N=1
    for i in range(level,num):
        f=sympy.expand(sympy.diff(f,var)/N)
        N=N+1
        res=res+sympy.limit(sympy.expand(f),var,point)*pow(var-point,i+1)

    return res

def print_time(str_, debug=True):
    if debug:
        print "\t\t\t time (%s) = %s"%(str_,time.time())
        sys.stdout.flush()
        
def print_debug(str_, debug=True):
    if debug:
        print str_
        sys.stdout.flush()


def RelativeError(expr, err, var):
    t_expr = expr
    t_err = err
    res = dict()
    idx = 0
    while(t_expr<>0):
        res[idx] = (t_err.subs(var,0),t_err.subs(var,0)/t_expr.subs(var,0))
        idx = idx + 1
        t_expr = t_expr.diff(var)/idx
        t_err = t_err.diff(var)/idx
    return res    


def moment_serialize(Moment, preserve_sign=False):
    t_moment=Moment
    atoms = t_moment.dict.keys()
    atoms.sort()
    if len(atoms)>0:
        if not preserve_sign and Moment.dict[atoms[0]] <0:
            t_moment= -t_moment
            atoms = t_moment.dict.keys()
            atoms.sort()
    res = ""
    for atom in atoms:
        res = res + str((atom, t_moment.dict[atom]))
    return res

def strech_serialize(strechs):
    res = ""
    keys = strechs.keys()
    keys.sort()
    for key in keys:
        vars = strechs[key]
        vars.sort()
        res = res + str((key,vars))
    return res

def diff_serialize(diffs):
    
    import copy
    keys = copy.copy(diffs)
    keys.sort()
    return str(keys)

def dot_serialize(dots):
    res = ""
    for dot in dots:
        res = res + str(("dot%s"%dot, dots[dot]))
    return res

def line_serialize(Line, include_dots=True): 
    s_moment = "moment:(%s)"%moment_serialize(Line.momenta, preserve_sign=False)
    
    if "strechs" in Line.__dict__:
        s_strechs = "strechs:(%s)"%strech_serialize(Line.strechs)
    else:
        s_strechs = "strechs:()"
        
    if "diffs" in Line.__dict__:
        s_diffs = "diffs:(%s)"%diff_serialize(Line.diffs)
    else:
        s_diffs = "diffs:()"
    
    s_dots = "dots:(%s)"%dot_serialize(Line.dots)
    if include_dots:
        return "line%s(%s,%s,%s,%s)"%(Line.type,s_moment,s_strechs,s_diffs,s_dots)
    else:
        return "line%s(%s,%s,%s)"%(Line.type,s_moment,s_strechs,s_diffs)

def node_serialize(Node):
    if Node.type == 0:
        s_moment = "" 
    elif Node.type == 1:
        s_moment = ""
    elif Node.type == 2:
        s_moment = moment_serialize(Node.lines_dict.values()[0].momenta, preserve_sign=False)
    elif Node.type == 3:
        s_moment = [moment_serialize(Node.lines_dict.values()[0].momenta, preserve_sign=False),moment_serialize(Node.lines_dict.values()[0].momenta, preserve_sign=False),moment_serialize(Node.lines_dict.values()[0].momenta, preserve_sign=False)]
        s_moment.sort()
    elif Node.type == 4:
        s_moment = moment_serialize(Node.lines_dict.values()[0].momenta, preserve_sign=False)
    else:
        raise ValueError, "Invalid node type: %s " %Node.type
    if "strechs" in Node.__dict__:
        s_strechs = "strechs:(%s)"%strech_serialize(Node.strechs)
    else:
        s_strechs = "strechs:()"
        
    if "diffs" in Node.__dict__:
        s_diffs = "diffs:(%s)"%diff_serialize(Node.diffs)
    else:
        s_diffs = "diffs:()"
    
    if "dots" in Node.__dict__:
        s_dots = "dots:(%s)"%dot_serialize(Node.dots)
    else:
        s_dots = "dots:()"
    
    return "node%s(%s,%s,%s,%s)"%(Node.type,s_moment,s_strechs,s_diffs,s_dots)

def graph_serialize(G):
    s_graph_dict=dict()
    for idxL in G.internal_lines:
        s_line=line_serialize(G.lines[idxL])
        if s_line in s_graph_dict.keys():
            s_graph_dict[s_line] =  s_graph_dict[s_line] + 1
        else:
            s_graph_dict[s_line] = 1
            
    for idxN in G.internal_nodes:
        s_node=node_serialize(G.nodes[idxN])
        if s_node in s_graph_dict.keys():
            s_graph_dict[s_node] =  s_graph_dict[s_node] + 1
        else:
            s_graph_dict[s_node] = 1
    
    keys = s_graph_dict.keys()
    keys.sort()
    
    res= ""
    for key in keys:
        res = res + str ((key, s_graph_dict[key]))
    
    return res



    
    
