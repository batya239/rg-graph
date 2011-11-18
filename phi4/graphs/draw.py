#!/usr/bin/python

import sys
from graphs import Graph

import pydot
    
G=pydot.Dot(graph_type="graph")

name=sys.argv[1]
g1=Graph(name)
cluster=g1.Cluster()
G.add_subgraph(cluster)
print G.to_string() 
open("pics/%s.png"%name, 'w').write(G.create_png())
