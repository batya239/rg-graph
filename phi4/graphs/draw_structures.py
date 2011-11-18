#!/usr/bin/python

import sys

from graphs import Graph
import pydot

structures=dict()

for line in open(sys.argv[1]).readlines():
    struct, diag=tuple(line.split(" "))
    if struct not in structures:
        structures[struct]=list()
    structures[struct].append(diag)
    
for struct in structures:
    G=pydot.Dot(graph_type="graph")
    for name in structures[struct]:
        name_=name[:-1]
        g1=Graph(name_)
        cluster=g1.Cluster()
        G.add_subgraph(cluster)
    open("pics/structures/%s.png"%struct.replace("**",'oo').replace("*", "_").replace("/", "v"), "w").write(G.create_png())
    
