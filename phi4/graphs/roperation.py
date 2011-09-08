#!/usr/bin/python
# -*- coding:utf8

def FindExternalAtoms(sub,moments):
    res=list()
    for line in sub.FindExternal()[1]:
        res=res+moments[line].strAtoms()
    return set(res)

def setStrech(sub,momets,atomsset)
    """ sub._strechvar must be set
    """
    for line in sub,_lines:
        atoms=set(moments[line].strAtoms() ) & atomsset
        for atom in atoms:
            if atom not in moments[line]._strech.keys:
                moments[line]._strech[atom]=[strechvar,]
            else:
                moments[line]._strech[atom].append(sub._strechvar)

def  strechMoments(graph,model):
    for sub in graph._subgraphs:
        dim = sub.Dim(model)
        if dim>0:
            sub._strechvar = "a_%s"%(sub.asLinesIdxStr())
            sub._diffcnt=dim+1
            extatoms=FindExternalAtoms(sub, graph._moments)
            setStrech(sub, graph._moments, extatoms)

            
            