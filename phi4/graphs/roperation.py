#!/usr/bin/python
# -*- coding:utf8

import sympy
import copy
import re as regex
import comb

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
        subgraphs=copy.copy(graph._subgraphs_m)
    else:
        subgraphs=copy.copy(graph._subgraphs)
    subgraphs.append(graph.asSubgraph())

    for sub in subgraphs:
        dim = sub.Dim(model)
        print "%s : %s"%(dim,sub)
        if dim>=0:
            sub._strechvar = "a_%s"%(sub.asLinesIdxStr())
            sub._diffcnt=dim+1
            extatoms=FindExternalAtoms(sub)
            setStrech(sub, extatoms)

def expr(graph, model):
    if "_subgraphs_m" in graph.__dict__:
        subgraphs=graph._subgraphs_m
    else:
        subgraphs=graph._subgraphs
    res=graph.expr(model)
    for sub in subgraphs:
        if "_strechvar" in sub.__dict__:
            res = res.diff(sympy.var(sub._strechvar), sub._diffcnt)
    g_as_sub=graph.asSubgraph()
    if graph.Dim(model)==0:
        strechvar=sympy.var("a_%s"%(graph.asSubgraph().asLinesIdxStr()))
        res=res.diff(strechvar, 2).subs(strechvar,0)
    return res
            
def det(graph,model):
        res=sympy.Number(1)
        d=sympy.var('d')
        for i in range(graph.NLoops()):
            res=res*sympy.var('q%s'%i)**(d-1)
        if model.space_dim - graph.NLoops()-2<0:
            raise ValueError, "Det not implemented: d=%s, nloops=%s "%(model.space_dim, graph.NLoops())
        for i in range(graph.NLoops()):
            for j in range(i+1,graph.NLoops()):
                res=res*sympy.var('st_%s_%s'%(i,j))**(d-3-i)
        return res

def subs_vars(graph):
        res=dict()
        jakob=sympy.Number(1)
        for i in range(graph.NLoops()):
            yi=sympy.var('y%s'%i)
            res['q%s'%i]=(1-yi)/yi
            jakob=jakob/yi/yi
            for j in range(i+1,graph.NLoops()):
                ct_ij=sympy.var('ct_%s_%s'%(i,j))
                res['ct_%s_%s'%(i,j)]=sympy.var('z_%s_%s'%(i,j))*2-1
                res['st_%s_%s'%(i,j)]=(1-ct_ij**2)**0.5
                jakob=jakob*2

                if i == 0:
                    res['q%sOq%s'%(i,j)]=eval('ct_%s_%s'%(i,j))
                elif  i == 1:
                    res['q%sOq%s'%(i,j)]=eval('ct_0_{1}*ct_0_{2}+st_0_{1}*st_0_{2}*ct_{1}_{2}'.format(i,j))
                elif  i == 2:
                    res['q%sOq%s'%(i,j)]=eval('ct_0_{1}*ct_0_{2}+st_0_{1}*st_0_{2}*(ct_1_{1}*ct_1_{2}+st_1_{1}*st_1_{2}*ct_{1}_{2})'.format(i,j))
                else:
                    raise NotImplementedError, "nloops>4"
        return jakob, res


def export_subs_vars(subs_vars):
    res=""
    for var in subs_vars:
        res=res + "double %s = %s;\n"%(var, sympy.printing.ccode(subs_vars[var]))
    return res

def FindExtCosAtoms(expr):
    atoms = expr.atoms(sympy.core.symbol.Symbol)
    atom_map = dict()
    for atom in atoms:
        reg1 = regex.match("^p\d*O(q\d+)$", str(atom))
        if reg1:
            atom_map[str(atom)]=reg1.groups()[0]
    return atom_map

def FindExtAtoms(expr):
    atoms = expr.atoms(sympy.core.symbol.Symbol)
    res = list()
    for atom in atoms:
        reg1 = regex.match("^(p\d*)$", str(atom))
        if reg1:
            res.append(reg1.groups()[0])
    return res

def SetAtomsToUnity(expr,str_atoms):
    res=expr
    for str_atom in str_atoms:
        res=res.subs(sympy.var(str_atom),1)
    return res

def AvgByExtDir(expr):
    def SetAtomsToZero(expr,str_atoms):
        res = expr
        for str_atom in str_atoms:
            res = res.subs(sympy.var(str_atom),0)
        return res

    atom_map=FindExtCosAtoms(expr)
    if len(atom_map.keys())==0:
        return expr
    else:
        d = sympy.var('d')
        res = SetAtomsToZero(expr, atom_map.keys())
        for selection in comb.xUniqueSelections(atom_map.keys(),2):
            atom1 = sympy.var(selection[0])
            atom2 = sympy.var(selection[1])
            atom12 = sympy.var("%sO%s"%tuple(sorted([atom_map[x] for x in selection])))
            t_expr = SetAtomsToZero(expr.diff(atom1).diff(atom2),atom_map.keys())
            if selection[0] == selection[1]:
                t_expr = t_expr/2./d
            else:
                t_expr = t_expr*atom12/d
            res = res+t_expr
        
        return SetAtomsToUnity(res, FindExtAtoms(expr))
