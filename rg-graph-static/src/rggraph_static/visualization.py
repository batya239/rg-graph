#!/usr/bin/python
# -*- coding: utf8

from model import Model
from graph import *
import pydot



def Graph2dot(G):
    strdot="digraph G {\n"
    #adding Nodes
    for idxN in G.Nodes:
        strdot=strdot+str(idxN)+"000 [ label=\"" +str(idxN)+"\""
        if "Graphviz" in G.model.NodeTypes[G.Nodes[idxN].Type]: 
            strdot=strdot+", "+G.model.NodeTypes[G.Nodes[idxN].Type]["Graphviz"]
        strdot=strdot+"];\n"
    #adding Lines
    for idxL in G.Lines:
        strdot=strdot+str(G.Lines[idxL].In)+"000 -> "+str(G.Lines[idxL].Out)+ "000 [label=\""+G.Lines[idxL].Momenta+" ("+str(idxL)+")\""
        if "Graphviz" in G.model.NodeTypes[G.Nodes[idxN].Type]: 
            strdot=strdot+", "+G.model.NodeTypes[G.Nodes[idxN].Type]["Graphviz"]
        strdot=strdot+"];\n"
    strdot=strdot+"}\n"
    return strdot

    