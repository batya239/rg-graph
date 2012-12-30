#!/usr/bin/python

import topology
import sys

valence=int(sys.argv[1])
nvertex=int(sys.argv[2])

topologies = [t for t in topology.GetTopologies({valence:nvertex})]

for t in topologies:
    print t

print
print len(topologies)

