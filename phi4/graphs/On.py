#!/usr/bin/python

import sys
import sympy

from dummy_model import _phi3,_phi4
from graphs import Graph
import utils
from copy import copy

def vertex_strucutre(lst):
    """ generate vertex strucutre for node. lst - list of line numbers (len=4 for phi4)
    """
#    print "lst=", lst
    if len(lst)<>4:
        raise ValueError,  "for phi4 model len(lst)==4 !!"
    a, b, c, d=tuple(lst)
    res=[[a, b, c, d], [a, c, b, d], [a, d, b, c]]
    
    sympy_res=sympy.Number(0)
    for term in res:
        d1, d2=sympy.var('d_%s_%s d_%s_%s'%tuple(term))
        sympy_res+=d1*d2
#    print sympy_res
    return sympy_res
    
def On(graph):
    res=sympy.Number(1)
    factor=sympy.Number(1)
    for node in graph.xInternalNodes():
        res=res*vertex_strucutre([i.idx() for i in node.Lines()])
        factor=factor/3
    for line in graph.ExternalLines():
        phi=sympy.var('phi_%s'%line.idx())
        res=res*phi
#    return utils.kronecker.contract(res)*factor
    return utils.kronecker.contract(res)
            


def reduce_to_r(expr):
    r=sympy.var('n,r1 r2 r3 r4 r5 r6 r7')
    n=r[0]
    r_map={n+2              :   r[1]*3,  
       n+8              :   r[2]*9,
       5*n+22           :   r[3]*27, 
       n*n+6*n+20       :   r[4]*27, 
       3*n*n+22*n+56    :   r[5]*81, 
       n*n+20*n+60      :   r[6]*81, 
       n*n*n+8*n*n+24*n+48: r[7]*81
       }
    res=expr
    if isinstance(expr, sympy.Mul):
        res=sympy.Number(1)
        for arg in expr.args:
            if isinstance(arg, sympy.Add):
                if arg in r_map.keys():
                    res=res*r_map[arg]
                else:
                    res=res*arg
            else:
                res=res*reduce_to_r(arg)
    elif isinstance(expr, sympy.Pow):
        arg1, arg2=expr.args
        res=reduce_to_r(arg1)**arg2
    elif isinstance(expr, sympy.Add):
        if expr in r_map.keys():
            return r_map[expr]
        else:
            return expr
    return res
        


phi4 = _phi4('dummy')
g1 = Graph(sys.argv[1])
O = On(g1)
#print O
#print
#print sympy.simplify(O)
#print
O1=sympy.factor(O)
print O1
phi__=sympy.var('phi')
O2=sympy.factor(O1.subs(phi__, 1))

#print O2,  type(O2), O2.args    
print reduce_to_r(O2)
