#!/usr/bin/python
# -*- coding: utf8
import sys
from dummy_model import _phi3,_phi4
from graphs import Graph


phi4=_phi4('dummy')

g1=Graph(sys.argv[1])


#phi4.reduce=False
name=str(g1.GenerateNickel())
print name, g1.sym_coef()