#!/usr/bin/python
# -*- coding:utf8

import sys
from sympy import *
import rggraph_static as rggrf



if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

from phi3 import *


print phi3.name

G = rggrf.Graph(phi3)
G.LoadLinesFromFile(filename)
G.DefineNodes({})
G.GenerateNickel()
print rggrf.nickel.Nickel(nickel=G.nickel.nickel).nickel
print rggrf.nickel.Nickel(nickel=G.nickel.nickel).edges
print G.sym_coeff

    

    