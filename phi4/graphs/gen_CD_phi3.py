#!/usr/bin/python
# -*- coding: utf8
import os

import graph_state
import sys
import polynomial

from methods.sd_tools import FeynmanSubgraphs
from dummy_model import _phi3

import dynamics
import graphs


model = _phi3("dummy")

g = graphs.Graph(sys.argv[1])
FeynmanSubgraphs(g, model)
g._subgraphs = []

C, D, E, T = dynamics.generateStaticCDET(g, model)
print "lines:"
for line in g._lines:
    print line
print "\nsubgraphs:"
for i in range(len(g._subgraphs)):
    print "a%s " % i, g._subgraphs

print "C = ", C
print "D = ", D

C_ = polynomial.poly([(1, x) for x in C])
D_ = polynomial.poly([(1, x) for x in D])

print
print "C = ", C_
print "D = ", D_



print "conservations = ", g._cons

#print "E = ", E
#print "T = ", T

