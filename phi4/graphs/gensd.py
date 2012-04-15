#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4

from graphs import Graph
import copy

phi4=_phi4('dummy')

#from sd import Prepare,  decompose,  poly_exp,  diff_poly_lst, set0_poly_lst, set1_poly_lst, poly_list2ccode,  strech_list, exp_pow
from sd import Prepare, save_sd
#from methods.feynman_tools import strech_indexes, dTau_line


#if len(sys.argv)==3:
#    exec('from %s import save, compile, execute'%sys.argv[2])
#else:
#    print "provide method"
#    sys.exit(1)

g1=Graph(sys.argv[1])
name=str(g1.GenerateNickel())
print name

#phi4.reduce=False
Prepare(g1,phi4)
print "nsectors=", len(g1._sectors)

save_sd(name, g1, phi4)


"""
print
print decompose([8, 9, 10, 11],[A1, ], g1._qi,  g1._cons )
print
print decompose([ 9, 10, 11, 8],[A1, ], g1._qi,  g1._cons )
"""

"""
print
print decompose([ 6, 7],[A1, A2, A3], g1._qi,  g1._cons )
print
print decompose([ 5, 7],[A1, A2, A3], g1._qi,  g1._cons )
print 
for term in diff_poly_lst(decompose([ 5, 7],[A1, A2, A3 ], g1._qi,  g1._cons )+[A4], 1000):
    print poly_list2ccode(term)
print set0_poly_lst(decompose([ 5, 7],[A1, A2, A3], g1._qi,  g1._cons ), 1000)
print set0_poly_lst(decompose([ 6, 7],[A1, A2, A3], g1._qi,  g1._cons ), 1000)
print
print set1_poly_lst(decompose([ 5, 7],[A1, A2, A3], g1._qi,  g1._cons ), 1000)
print set1_poly_lst(decompose([ 6, 7],[A1, A2, A3], g1._qi,  g1._cons ), 1000)
"""
