#!/usr/bin/python
# -*- coding:utf8

def FindExternalAtoms(sub):
    res=list()
    for line in sub.FindExternal()[1]:
        res=res+line.momenta.strAtoms()
    return set(res)

def setStrech(sub,atomsset):
    """ sub._strechvar must be set
    """
    for line in sub._lines:
        atoms=set(line.momenta.strAtoms() ) & atomsset
        for atom in atoms:
            if atom not in line.momenta._strech.keys():
                line.momenta._strech[atom]=[sub._strechvar,]
            else:
                line.momenta._strech[atom].append(sub._strechvar)

def  strechMoments(graph,model):
    if "_subgraphs_m" in graph.__dict__:
        subgraphs=graph._subgraphs_m
    else:
        subgraphs=graph._subgraphs
    subgraphs.append(graph.asSubgraph())

    for sub in subgraphs:
        dim = sub.Dim(model)
        print "%s : %s"%(dim,sub)
        if dim>=0:
            sub._strechvar = "a_%s"%(sub.asLinesIdxStr())
            sub._diffcnt=dim+1
            extatoms=FindExternalAtoms(sub)
            setStrech(sub, extatoms)


            
            