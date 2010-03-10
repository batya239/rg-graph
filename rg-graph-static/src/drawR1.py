#!/usr/bin/python
# -*- coding:utf8
import sys
from sympy import *
import rggraph_static as rggrf
#import pydot
import copy
from rggraph_static.utils import print_time

print_time("start")

if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

from phi3 import *


print phi3.name

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.DefineNodes({})
G.SaveAsPNG("graph.png")
G_list = []
R1_list = []
print_time("define nodes")
G.GenerateNickel()
print_time("nickel")
base_name = str(G.nickel)
TARGET = 4
NLOOPS = len(G.internal_lines) - len(G.internal_nodes) + 1
print "NLOOPS = " , NLOOPS
#print len(G.internal_lines) , len(G.internal_nodes)
n_epsilon_series = TARGET - NLOOPS
NPOINTS = 10000
NTHREADS = 2 
SPACE_DIM = 6.

for idxL in G.internal_lines:
    print_time("line %s" %idxL)
    cur_G = G.Clone()
    cur_G.lines[idxL].dots[1] = 1
    cur_G.DefineNodes()
    print_time("define nodes")
    cur_G.FindSubgraphs()
    print_time("Find subgraphs")
    cur_r1 = rggrf.roperation.R1(cur_G)
    print_time("r operation done")
    cur_r1.SaveAsPNG("R1_%s_dm%s.png" %(base_name, idxL))
