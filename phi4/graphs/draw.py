#!/usr/bin/python

import sys
from graphs import Graph

import pydot

#lines=[]
#nodes=dict()
#ext_cnt=0
#for line in g1._lines:
#    nodes_ = line.start, line.end
#    print nodes_
#    nodes__=list()
#    for node in nodes_:
#        print node
#        if node.isInternal():
#            nodes__.append(("%s_%s"%(name, node.idx()), "%s"%node.idx()))
#        else:
#            nodes__.append(("%s_%s_%s"%(name, node.idx(), ext_cnt), "ext"))
#            ext_cnt+=1
#        if nodes__[-1][0] not in nodes.keys():
#            nodes[nodes__[-1][0]]=nodes__[-1][1]
#    print nodes__
#    lines.append([n[0] for n in nodes__])
#        
#print lines
#print nodes
#    
#
#cluster=pydot.Cluster(name.replace("-", "_"))

    
G=pydot.Dot(graph_type="graph")

name=sys.argv[1]
g1=Graph(name)
cluster=g1.Cluster()
G.add_subgraph(cluster)
print G.to_string() 
open("%s.png"%name, 'w').write(G.create_png())
