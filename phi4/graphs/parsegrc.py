#!/usr/bin/python
# -*- coding: utf8

import utils
from dummy_model import _phi3,_phi4
import sys
from graphs import Graph

phi4=_phi4('dummy')

for nickel in utils.LoadFromGRC(sys.argv[1], phi4):
    g=Graph(nickel)
    g.GenerateNickel()
    print "%s %s"%(nickel, g.sym_coef())