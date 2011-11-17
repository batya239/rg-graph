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
    return utils.kronecker.contract(res)*factor
            


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
print sympy.factor(O1.subs(phi__, 1))

