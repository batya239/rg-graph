#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

workdir = "akkuratova/rg-graph/phi4/graphs/phi4_dyn/simpleSDT"
libdir = "libs/pvegas"
mpidir = "/usr/lib64/openmpi/1.4-gcc"
nodes = "16"
nodesppn = "%s:ppn=4" % nodes
iterations = 2
delta = 0.
points = 100000