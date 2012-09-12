#!/usr/bin/python
import nickel
from nodes import Node
import subgraphs
import itertools

__author__ = 'mkompan'

import sys
from graphs import Graph
from dummy_model import _phi4


model=_phi4('dummy')

graph=Graph(sys.argv[1])
graph.GenerateNickel()

model.SetTypes(graph)
model.checktadpoles = False
graph.FindSubgraphs(model)

subgraphs.RemoveTadpoles(graph)
#print graph

#print [str(nickel.Canonicalize(x.ToEdges())) for x in  graph._subgraphs]

def overlap(sub1,sub2):
    nodes1=sub1.InternalNodes()
    nodes2=sub2.InternalNodes()
    return len(set(sub1._lines)&set(sub2._lines))<>0 or len(set(nodes1)&set(nodes2))<>0


def ReduceSubgraphs(graph, subs):
    g=graph.Clone()
#    print subs
#    print graph._subgraphs
    subs_=map(lambda x: g._subgraphs[graph._subgraphs.index(x)], subs)
    nodeidx=1000
    for sub in subs_:
        print sub
        print g
        extnodes,extlines=sub.FindExternal()
        if len(extlines)<>4:
            raise ValueError, "can't Reduce self energy subgraph"
        for line in sub._lines:
            g.RemoveLine(line)

        for node in sub.InternalNodes():
            g.RemoveNode(node)

        print extlines
        extnodes_=list()
        for line in extlines:
            node=set(line.Nodes())&set(extnodes)
            if len(node)==1:
                extnodes_+=list(node)
            else:
                raise ValueError, "...."
#            print line, g._lines
#            g.RemoveLine(line)

        print extnodes_
        newnode=Node()
        for node in extnodes_:
            newnode.AddLine(node)

        g.AddNode(newnode)
    return g

def sub_edges(sub):
    res=list()
    for line in sub._lines:
        res.append(map(lambda x: x.idx(), line.Nodes()))
    return res

def find_sub_by_node(node_idx, snodes):
    for i in range(len(snodes)):
#        print node_idx, snodes[i], node_idx in snodes[i]
        if node_idx in snodes[i]:
            return i+1000
    return node_idx


def ReducedGraph(graph,subs):
    """
    assumes that no tadpole subgraphs here
    """
    ge=graph._edges()
    newge=list()
    snodes=[map(lambda y: y.idx(), x.InternalNodes()) for x in subs]
    slines=nickel.flatten([sub_edges(x)  for x in subs])

#    print ge
#    print snodes
#    print slines
    for line in ge:
#        print line, slines
        if line in slines:
            continue

        node1,node2=line
        node1_=find_sub_by_node(node1,snodes)
        node2_=find_sub_by_node(node2,snodes)
#        print node1,node2, " ", node1_, node2_
        newge.append([node1_,node2_])

    return str(nickel.Canonicalize(newge))



#print ReducedGraph(graph, [graph._subgraphs[0]])

r1=dict()

for i in range(1,len(graph._subgraphs)+1):
    for subs in itertools.combinations(graph._subgraphs,i):
        valid=True
        for subs2 in itertools.combinations(subs,2):
            if overlap(subs2[0],subs2[1]):
                valid=False
                break

        if valid:
#            print "---"
#               print subs
            gnickel=ReducedGraph(graph, subs)

            term="'%s', %s"%(gnickel, tuple([str(x.Nickel())     for x in subs]))
            sign=(-1)**(len(subs)+1)
            if not r1.has_key(term):
                r1[term]=sign
            else:
                r1[term]+=sign

print "gamma='%s'"%graph.nickel
print "R1op=["
for term in r1:
    print "    (%s, %s),"%(r1[term],term)
print "]"
print "KR(gamma, R1op, %s)\nprintKR1(gamma)"%graph.NLoops()

