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
#            print str_ext_cos_atoms
            for atom in str_ext_cos_atoms:
                s_atom = var(atom)
                t_expr = t_expr.subs(s_atom, 0)
            res = res + t_expr
#            print s_atom, t_expr
        if degree >=2:
            
            for selection in utils.xUniqueSelections(list(str_ext_cos_atoms), 2):
#                print selection
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
                    

def Prepare(k_op, space_dim):
# TODO: p=1 m=1 Надо делать в каком-то другом месте, до того как выражение попадает сюда
# TODO: усреднение по направлениям p (eps)
# TODO: детерминанант по модулям (eps)
# TODO: инверсия по модулям (0-inf) -> (0 - 1)
# TODO: замена косинусов и детерминант по углам
# TODO: разложение в ряд по eps
# TODO: вывод.    

    def g_cos(idx1, idx2, vars_dict):
        print vars_dict
        return vars_dict["ct_%s_%s" %(idx1,idx2)]
    def g_sin(idx1, idx2, vars_dict):
        return (1-g_cos(idx1,idx2,vars_dict)**2)**0.5 

    expr = k_op
    str_atom_set = ginac.GetVarsAsStr(k_op)
    (ext_moment_atoms, ext_cos_atoms, int_moment_atoms, 
                       int_cos_atoms, other_atoms) = SplitAtoms(str_atom_set)
    if len(ext_moment_atoms | other_atoms)>0:
        raise  NotImplementedError, "Don't know what to do with following atoms: %s" %(ext_moment_atoms|other_atoms)
    expr = AvarageByExtDirection(expr, ext_cos_atoms, 2)
    (g_expr, g_vars) = ginac.sympy2swiginac(expr)

# доопределяем недостающие переменные самое важное d и e, остальное на самом деле вроде не нужно.
    for idx in ["d", "e"]+list(int_moment_atoms)+list(int_cos_atoms):
        if  idx not in g_vars:
            g_vars[idx] = swiginac.symbol(idx)
            
# общий знаменатель
    g_expr = swiginac.normal(g_expr)

    d = g_vars["d"]
# детерминанты по импульсам
    for int_moment in list(int_moment_atoms):
        g_expr = g_expr * g_vars[int_moment] ** ( d - 1)
        
#Инверсия
    inv_moments = set([])
    for idx in list(int_moment_atoms):
        reg = regex.match("^q(\d+)$",idx)
        if reg:
            t_inv = "y%s" %reg.groups()[0]
            inv_moments = inv_moments | set([t_inv,])
            g_vars[t_inv] = swiginac.symbol(t_inv)
            g_expr = g_expr.subs(g_vars[idx] == (1 - g_vars[t_inv]) / g_vars[t_inv]) / g_vars[t_inv] / g_vars[t_inv] 
        else:
            raise ValueError, "Unknown internal momenta %s" %idx 
        
#замена на полярные углы

#    n>=1
#q0 x qn = ct_0_n
#(1-ct_0_n**2)**((d-3)/2)
#
#    n>=2
#q1 x qn =  ct_0_1*ct_0_n+ ( 1 - ct_0_1**2)**(0.5)*(1-ct_0_n**2)**(0.5)*ct_1_n
#q1 x qn =  ct_0_1*ct_0_n+ sin_0_1*sin_0_n*ct_1_n    
#(1-ct_1_n**2)**((d-4)/2)
#
#    n>=3
#q2 x qn = ct_0_2*ct_0_n+(1-ct_0_2**2)**0.5*(1-ct_0_n**2)**0.5*(ct_1_2*ct_1_n+(1-ct_1_2**2)**0.5*(1-ct_1_n*2)*0.5)*ct_2_n)
#q2 x qn = ct_0_2*ct_0_n+sin_0_2*sin_0_n*(ct_1_2*ct_1_n+sin_1_2*sin_1_n*ct_2_n)
#(1-ct_2_n**2)**((d-5)/2)

#define polar cosines in swiginac
    polar_cos = set([])
    int_moment_atoms_list = list(int_moment_atoms)
    for idx1 in range(len(int_moment_atoms_list)):
        for idx2 in range(idx1+1,len(int_moment_atoms_list)):
            t_polar_cos = "ct_%s_%s" % (idx1,idx2)
            g_vars[t_polar_cos] = swiginac.symbol(t_polar_cos)
            polar_cos = polar_cos | set([t_polar_cos,])
    
    for atom in int_cos_atoms:
        reg = regex.match("(q\d+)x(q\d+)",atom)
        if reg:
            idx1 = int_moment_atoms_list.index(reg.groups()[0])
            idx2 = int_moment_atoms_list.index(reg.groups()[1])
            if idx1 > idx2:
                idx1, idx2 = idx2, idx1
            if space_dim - idx1 -3 < 0:
                raise NotImplementedError, " number of independent moments more then d-2 . d = %s" %space_dim
             
            if idx1 == 0 :
                det = g_sin(idx1, idx2, g_vars)  ** (d - 3) 
                subst = g_cos(idx1, idx2, g_vars)
            elif idx1 == 1 :
                det = g_sin(idx1, idx2, g_vars) ** (d - 4)
                subst = (g_cos(0, idx1, g_vars) * g_cos(0, idx2, g_vars) +
                         g_sin(0, idx1, g_vars) * g_sin(0, idx2, g_vars) * 
                         g_cos(idx1, idx2, g_vars))
            elif idx1 == 2 :
                det = g_sin(idx1, idx2, g_vars) ** (d - 5)
                subst = (g_cos(0, idx1, g_vars) * g_cos(0, idx2, g_vars) +
                         g_sin(0, idx1, g_vars) * g_sin(0, idx2, g_vars) *
                         (g_cos(1, idx1, g_vars) * g_cos(1, idx2, g_vars) +
                         g_sin(1, idx1, g_vars) * g_sin(1, idx2, g_vars) * 
                         g_cos(idx1, idx2, g_vars)))
            else:
                raise NotImplementedError, " number of independent moments more then d-2 . d = %s" %space_dim

            g_expr = g_expr.subs(g_vars[atom] == subst) * det
        else:
            raise ValueError,  "Unknown scalar product of internal moments  %s " %atom
                

    
    return (g_expr,g_vars)


