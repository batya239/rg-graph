#!/usr/bin/python
# -*- coding: utf8

'''
Created on Feb 19, 2010

@author: mkompan
'''
import swiginac
import ginac
import utils
import re as regex
from sympy import *

def SplitAtoms(str_atom_set):
    import re
    ext_moment_atoms = []
    ext_cos_atoms = []
    int_moment_atoms = []
    int_cos_atoms = []
    other_atoms = []
    for atom in list(str_atom_set):
        if re.match('^p\d*$', atom):
            ext_moment_atoms.append(atom)
        elif re.match('^p\d*x.+', atom) or re.match('.+xp\d*$', atom):
            ext_cos_atoms.append(atom)
        elif re.match('^q\d+$', atom):
            int_moment_atoms.append(atom)
        elif re.match('^q\d+xq\d+', atom):
            int_cos_atoms.append(atom)
        else:
            other_atoms.append(atom)
    
    return (set(ext_moment_atoms), set(ext_cos_atoms), set(int_moment_atoms),
                                   set(int_cos_atoms), set(other_atoms))

def AvarageByExtDirection(s_expr,str_ext_cos_atoms,degree):
#TODO: need lots of verifications to work in general case now only 0 and 2
    res = 0
    d = var('d')
    if degree not in [0,2]:
        raise NotImplementedError, "AvarageByExtDirection for %s degree of external momenta not implemented" %degree
    else:
        if degree >=0:
            t_expr = s_expr
            print str_ext_cos_atoms
            for atom in str_ext_cos_atoms:
                s_atom = var(atom)
                t_expr = t_expr.subs(s_atom, 0)
            res = res + t_expr
            print s_atom, t_expr
        if degree >=2:
            
            for selection in utils.xUniqueSelections(list(str_ext_cos_atoms), 2):
                print selection
                t_expr = s_expr
                t_lst = []
                for idx in selection:

                    reg1 = regex.match("^p\d*x(q\d+)$",idx)
                    if reg1:
                        t_lst.append(reg1.groups()[0])
                        
                    reg2 = regex.match("^(q\d+)xp\d*$",idx)
                    if reg2:
                        t_lst.append(reg2.groups()[1])
                t_lst.sort()
                atom1 = var(selection[0])        
                atom2 = var(selection[1])
                atom12 = var("%sx%s"%(t_lst[0],t_lst[1]))
                
#                print atom1,atom2,atom12
#                print t_expr.diff(atom2)
                t_expr = t_expr.diff(atom1).diff(atom2).subs(atom1, 0).subs(atom2, 0)
                if selection[0] == selection[1]:
                    t_expr = t_expr/2/d
                else:
                    t_expr = t_expr*atom12/d
#            print t_expr
            res = res + t_expr
        return res
                    

def Prepare(k_op, space_dim, n_epsilon_series):
# TODO: p=1 m=1 Надо делать в каком-то другом месте, до того как выражение попадает сюда
# TODO: усреднение по направлениям p (eps)
# TODO: детерминанант по модулям (eps)
# TODO: инверсия по модулям (0-inf) -> (0 - 1)
# TODO: разложение в ряд по eps
# TODO: вывод.    
    expr = k_op
    str_atom_set = ginac.GetVarsAsStr(k_op)
    (ext_moment_atoms, ext_cos_atoms, int_moment_atoms, 
                       int_cos_atoms, other_atoms) = SplitAtoms(str_atom_set)
    if len(ext_moment_atoms | other_atoms)>0:
        raise  NotImplementedError, "Don't know what to do with following atoms: %s" %(ext_moment_atoms|other_atoms)
    expr = AvarageByExtDirection(expr, ext_cos_atoms, 2)
    
    return expr

