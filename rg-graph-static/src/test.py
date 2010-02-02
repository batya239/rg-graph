#!/usr/bin/python
# -*- coding:utf8

from sympy import *
import rggraph_static as rggrf
print dir(rggrf)
print dir(rggrf.Model)
var('p tau p1')

phi3=rggrf.Model("phi3")
phi3.addLineType(1,propagator=1/(p*p+tau),directed=0)

phi3.addNodeType(0,Lines=[],Factor=1)  #External Node
phi3.addNodeType(1,Lines=[1,1,1],Factor=1)
phi3.addNodeType(2,Lines=[1,1],Factor=p1*p1)

print phi3
