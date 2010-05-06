#!/usr/bin/python
# -*- coding: utf8

'''
Created on Feb 19, 2010

@author:mkompan
'''
import swiginac
import ginac
import utils
import re as regex
from sympy import *
import subprocess


def SplitAtoms(str_atom_set):
    ext_moment_atoms = []
    ext_cos_atoms = []
    int_moment_atoms = []
    int_cos_atoms = []
    other_atoms = []
    for atom in list(str_atom_set):
        if regex.match('^p\d*$', atom):
            ext_moment_atoms.append(atom)
        elif regex.match('^p\d*x.+', atom) or regex.match('.+xp\d*$', atom):
            ext_cos_atoms.append(atom)
        elif regex.match('^q\d+$', atom):
            int_moment_atoms.append(atom)
        elif regex.match('^q\d+xq\d+', atom):
            int_cos_atoms.append(atom)
        else:
            other_atoms.append(atom)
    
    return (set(ext_moment_atoms), set(ext_cos_atoms), set(int_moment_atoms),
                                   set(int_cos_atoms), set(other_atoms))

def AvarageByExtDirection(s_expr, str_ext_cos_atoms, degree, debug=False):
    
    def SetAtomsToZero(expr,str_atoms):
        res = expr
        for str_atom in str_atoms:
            atom = var(str_atom)
            res = res.subs(atom,0)
#        print "Set Zero: %s "%str_atoms
#        pretty_print(res)
        return res
#TODO: need lots of verifications to work in general case; now only 0 and 2 degree
#    print "==== AvarageByExtDirection "
#    print str_ext_cos_atoms,degree
    res = 0
    d = var('d')
    if degree not in [0,2]:
        raise NotImplementedError, "AvarageByExtDirection for %s degree of external momenta not implemented" %degree
    else:
        if degree >=0:
            t_expr = s_expr
#            print str_ext_cos_atoms
            t_expr = SetAtomsToZero(t_expr,str_ext_cos_atoms)
#            print "degree 0 ", t_expr
            res = res + t_expr
#            print s_atom, t_expr
        if degree >=2:
#            print "degree2"
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
#                print "t_lst = %s"%t_lst
                atom1 = var(selection[0])        
                atom2 = var(selection[1])
                atom12 = var("%sx%s"%(t_lst[0],t_lst[1]))
                
#                print atom1,atom2,atom12
#                print t_expr.diff(atom2)
                t_expr = SetAtomsToZero(t_expr.diff(atom1).diff(atom2),str_ext_cos_atoms)
                if selection[0] == selection[1]:
                    t_expr = t_expr/2./d
                else:
                    t_expr = t_expr*atom12/d
                
#            print t_expr
                res = res + t_expr
        return res
    

def PrepareFactorizedStrVars(fact_expr, space_dim, ignore_unknown=False, simplify = False, debug = False):
# TODO: p=1 m=1 Надо делать в каком-то другом месте, до того как выражение попадает сюда
# TODO: усреднение по направлениям p (eps)
# TODO: детерминанант по модулям (eps)
# TODO: инверсия по модулям (0-inf) -> (0 - 1)
# TODO: замена косинусов и детерминант по углам
# TODO: разложение в ряд по eps
# TODO: вывод.    

    def g_cos(idx1, idx2, vars_dict):
        return vars_dict["ct_%s_%s" %(idx1,idx2)]
    def g_sin(idx1, idx2, vars_dict):
        return (1-g_cos(idx1,idx2,vars_dict)**2)**0.5
    str_vars = "" 
    utils.print_time("Prepare: start", debug)
#    expr = k_op
    str_atom_set = ginac.GetVarsAsStr(fact_expr.factor * fact_expr.other)
    (ext_moment_atoms, ext_cos_atoms, int_moment_atoms, 
                       int_cos_atoms, other_atoms) = SplitAtoms(str_atom_set)
    strech_atoms = set([])
    if ignore_unknown:
        pass
    else:
        if len(ext_moment_atoms | other_atoms)>0:
            unknown_atoms = ext_moment_atoms | other_atoms
            strech_atoms = set([])
            for atom in unknown_atoms:
                if regex.match("^a_", atom):
                    strech_atoms = strech_atoms | set([atom,])
            if len(unknown_atoms - strech_atoms-set(['e','pi']))>0:
                raise  NotImplementedError, "Don't know what to do with following atoms: %s" %(unknown_atoms - strech_atoms-set(['eps','pi']))
    #print ext_cos_atoms
    expr_o = AvarageByExtDirection(fact_expr.other, ext_cos_atoms, 2, debug=debug)
    #pretty_print(expr_o) 
#    print "\nExtDir:\n"
#    pretty_print(expr)

# TODO: search for int_cos_atoms again it changed after avaraging 
    int_cos_atoms = set([])
    for idxM1 in int_moment_atoms:
        for idxM2 in int_moment_atoms:
            if idxM1<idxM2:
                int_cos_atoms = int_cos_atoms | set(["%sx%s"%(idxM1,idxM2),])

    (g_expr_f,g_expr_o, g_vars) = ginac.sympy2swiginacFactorized(fact_expr.factor,expr_o)

                
# доопределяем недостающие переменные самое важное d и e, остальное на самом деле вроде не нужно.
    for idx in ["d", "e"]+list(int_moment_atoms)+list(int_cos_atoms) + list(strech_atoms):
        if  idx not in g_vars:
            g_vars[idx] = swiginac.symbol(idx)
    utils.print_time("Prepare:before normal",debug)        
# общий знаменатель
    if simplify:
        g_expr = g_expr_f * swiginac.normal(g_expr_o)
    else:
        g_expr = g_expr_f * g_expr_o    
    utils.print_time("Prepare:after normal ",debug)
    
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
            g_subs = (1. - g_vars[t_inv]) / g_vars[t_inv]
            g_expr = g_expr/ g_vars[t_inv] / g_vars[t_inv]
            str_vars = "%s\n double q%s = %s;"%(str_vars, reg.groups()[0],g_subs.printc())
#            g_expr = g_expr.subs(g_vars[idx] == (1 - g_vars[t_inv]) / g_vars[t_inv]) / g_vars[t_inv] / g_vars[t_inv] 
        else:
            raise ValueError, "Unknown internal momenta %s" %idx
    utils.print_time("Prepare: inversion",debug)
        
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
#            print "\n\n subst = %s\n det = %s\n\n" %(subst, det)

            str_vars =  "%s\n double %s = %s;"%(str_vars, atom, subst.printc())
            g_expr = g_expr * det
            
        else:
            raise ValueError,  "Unknown scalar product of internal moments  %s " %atom
    utils.print_time("Prepare: end",debug)  


    return (g_expr,g_vars,str_vars)


def PrepareFactorized(fact_expr, space_dim, ignore_unknown=False, simplify = False):
# TODO: p=1 m=1 Надо делать в каком-то другом месте, до того как выражение попадает сюда
# TODO: усреднение по направлениям p (eps)
# TODO: детерминанант по модулям (eps)
# TODO: инверсия по модулям (0-inf) -> (0 - 1)
# TODO: замена косинусов и детерминант по углам
# TODO: разложение в ряд по eps
# TODO: вывод.    

    def g_cos(idx1, idx2, vars_dict):
        return vars_dict["ct_%s_%s" %(idx1,idx2)]
    def g_sin(idx1, idx2, vars_dict):
        return (1-g_cos(idx1,idx2,vars_dict)**2)**0.5
    str_vars = "" 
    utils.print_time("Prepare: start")
#    expr = k_op
    str_atom_set = ginac.GetVarsAsStr(fact_expr.factor * fact_expr.other)
    (ext_moment_atoms, ext_cos_atoms, int_moment_atoms, 
                       int_cos_atoms, other_atoms) = SplitAtoms(str_atom_set)

    if ignore_unknown:
        pass
    else:
        if len(ext_moment_atoms | other_atoms)>0:
            raise  NotImplementedError, "Don't know what to do with following atoms: %s" %(ext_moment_atoms|other_atoms)

    expr_o = AvarageByExtDirection(fact_expr.other, ext_cos_atoms, 2)
#    print "\nExtDir:\n"
#    pretty_print(expr)

# TODO: search for int_cos_atoms again it changed after avaraging 
    int_cos_atoms = set([])
    for idxM1 in int_moment_atoms:
        for idxM2 in int_moment_atoms:
            if idxM1<idxM2:
                int_cos_atoms = int_cos_atoms | set(["%sx%s"%(idxM1,idxM2),])
    (g_expr_f,g_expr_o, g_vars) = ginac.sympy2swiginacFactorized(fact_expr.factor,expr_o)
#    print g_vars
#    print int_cos_atoms

# доопределяем недостающие переменные самое важное d и e, остальное на самом деле вроде не нужно.
    for idx in ["d", "e"]+list(int_moment_atoms)+list(int_cos_atoms):
        if  idx not in g_vars:
            g_vars[idx] = swiginac.symbol(idx)
    utils.print_time("Prepare:before normal")        
# общий знаменатель
    if simplify:
        g_expr = g_expr_f * swiginac.normal(g_expr_o)
    else:
        g_expr = g_expr_f * g_expr_o 
        
    utils.print_time("Prepare:after normal ")
    
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
            g_subs = (1 - g_vars[t_inv]) / g_vars[t_inv]
            g_expr = g_expr.subs(g_vars[idx] == (1 - g_vars[t_inv]) / g_vars[t_inv]) / g_vars[t_inv] / g_vars[t_inv] 
        else:
            raise ValueError, "Unknown internal momenta %s" %idx
    utils.print_time("Prepare: inversion")
        
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
#            print "\n\n subst = %s\n det = %s\n\n" %(subst, det)

            g_expr = g_expr.subs(g_vars[atom] == subst) * det
        else:
            raise ValueError,  "Unknown scalar product of internal moments  %s " %atom
    utils.print_time("Prepare: end")  

    
    return (g_expr,g_vars)



def Prepare(k_op, space_dim):
# TODO: p=1 m=1 Надо делать в каком-то другом месте, до того как выражение попадает сюда
# TODO: усреднение по направлениям p (eps)
# TODO: детерминанант по модулям (eps)
# TODO: инверсия по модулям (0-inf) -> (0 - 1)
# TODO: замена косинусов и детерминант по углам
# TODO: разложение в ряд по eps
# TODO: вывод.    

    def g_cos(idx1, idx2, vars_dict):
        return vars_dict["ct_%s_%s" %(idx1,idx2)]
    def g_sin(idx1, idx2, vars_dict):
        return (1-g_cos(idx1,idx2,vars_dict)**2)**0.5 
    utils.print_time("Prepare: start")
    expr = k_op
    str_atom_set = ginac.GetVarsAsStr(k_op)
    (ext_moment_atoms, ext_cos_atoms, int_moment_atoms, 
                       int_cos_atoms, other_atoms) = SplitAtoms(str_atom_set)
    if len(ext_moment_atoms | other_atoms)>0:
        raise  NotImplementedError, "Don't know what to do with following atoms: %s" %(ext_moment_atoms|other_atoms)
    expr = AvarageByExtDirection(expr, ext_cos_atoms, 2)
    
# TODO: search for int_cos_atoms again it changed after avaraging 
    (ext_moment_atoms, ext_cos_atoms, int_moment_atoms, 
                       int_cos_atoms, other_atoms) = SplitAtoms(ginac.GetVarsAsStr(expr))
#    print "\nExtDir:\n"
#    pretty_print(expr)
    (g_expr, g_vars) = ginac.sympy2swiginac(expr)
#    print g_vars
#    print int_cos_atoms
# доопределяем недостающие переменные самое важное d и e, остальное на самом деле вроде не нужно.
    for idx in ["d", "e"]+list(int_moment_atoms)+list(int_cos_atoms):
        if  idx not in g_vars:
            g_vars[idx] = swiginac.symbol(idx)
    utils.print_time("Prepare:before normal")        
# общий знаменатель
    g_expr = swiginac.normal(g_expr)
    utils.print_time("Prepare:after normal ")
    
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
    utils.print_time("Prepare: inversion")
# TODO: это приведение к общ. знаменателю может занимать много времени 
# общий знаменатель
#    g_expr = swiginac.normal(g_expr)
    
        
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
#            print "\n\n subst = %s\n det = %s\n\n" %(subst, det)
            g_expr = g_expr.subs(g_vars[atom] == subst) * det
        else:
            raise ValueError,  "Unknown scalar product of internal moments  %s " %atom
    utils.print_time("Prepare: end")  

    
    return (g_expr,g_vars)

def SavePThreadsMCCode(name, c_expr, c_vars, str_region, points, nthreads):
    template = '''
    
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>

#define DIMENSION <-DIMENSION->
#define FUNCTIONS 1
#define ITERATIONS <-ITERATIONS->
#define NTHREADS <-NTHREADS->
#define NEPS 0
#ifndef PI
#define PI     3.14159265358979323846
#endif
double reg[2*DIMENSION]= <-REGION->;
void func (double k[DIMENSION], double f[FUNCTIONS]) {
double Pi=PI;
<-VARS->
f[0]=<-INTEGRAND->;  }




int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{
  int i;
  long long npoints;
  int nthreads;
  if(argc >= 2)
    {
      npoints = atoll(argv[1]);

    }
  else 
    {
      npoints = ITERATIONS;
    }

  if(argc >= 3)
    {
      nthreads = atoi(argv[2]);

    }
  else 
    {
      nthreads = NTHREADS;
    }
    
  if(argc >= 4)
    {
      niter = atoi(argv[3]);

    }
  else 
    {
      niter = NITER;
    }
    
  double estim[FUNCTIONS];   /* estimators for integrals                     */
  double std_dev[FUNCTIONS]; /* standard deviations                          */
  double chi2a[FUNCTIONS];   /* chi^2/n                                      */

  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
double delta= std_dev[0]/estim[0];
printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\n", estim[0], std_dev[0], delta);
//  printf ("Result %d: %g +/- %g delta=%g\\n",NEPS, estim[0], std_dev[0], delta);
//  for (i=1; i<FUNCTIONS; ++i)
//    printf("Result %i:\\t%g +/- %g  \\tdelta=%g\\n", i, estim[i], std_dev[i],std_dev[i]/estim[i]);
  return(0);
}
    '''
    res = template.replace("<-DIMENSION->", str(len(str_region.split(","))/2))
    res = res.replace("<-ITERATIONS->", str(int(points)))
    res = res.replace("<-NTHREADS->",str(int(nthreads)))
    res = res.replace("<-REGION->",str_region)
    res = res.replace("<-VARS->",c_vars)
    
    res = res.replace("<-INTEGRAND->",c_expr)
    file = open(name+".c", 'w')
    file.write(res)
    file.close()

def SavePThreadsMCCodeDelta(name, c_expr, c_vars, str_region, points, nthreads):
    template = '''
    
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>

#define DIMENSION <-DIMENSION->
#define FUNCTIONS 1
#define ITERATIONS <-ITERATIONS->
#define NTHREADS <-NTHREADS->
#define NITER 2
#define NEPS 0
#ifndef PI
#define PI     3.14159265358979323846
#endif
double reg_initial[2*DIMENSION]= <-REGION->;
void func (double k[DIMENSION], double f[FUNCTIONS]) {
double Pi=PI;
<-VARS->
f[0]=<-INTEGRAND->;  }



int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{
  int i;
  long long npoints;
  int nthreads;
  int niter;
  double region_delta;
  double reg[2*DIMENSION];
  int idx;
  if(argc >= 2)
    {
      npoints = atoll(argv[1]);

    }
  else 
    {
      npoints = ITERATIONS;
    }

  if(argc >= 3)
    {
      nthreads = atoi(argv[2]);

    }
  else 
    {
      nthreads = NTHREADS;
    }
   
   if(argc >= 5)
    {
      region_delta = atof(argv[4]);

    }
  else 
    {
      region_delta = 0.;
    } 

  if(argc >= 4)
    {
      niter = atoi(argv[3]);

    }
  else 
    {
      niter = NITER;
    }    
    
    for(idx=0; idx<2*DIMENSION; idx++)
      {
         if(idx<DIMENSION)
           {
             reg[idx] = reg_initial[idx]+region_delta;
           }
         else
           {
             reg[idx] = reg_initial[idx]-region_delta;
           }
      }
      
  double estim[FUNCTIONS];   /* estimators for integrals                     */
  double std_dev[FUNCTIONS]; /* standard deviations                          */
  double chi2a[FUNCTIONS];   /* chi^2/n                                      */

  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
double delta= std_dev[0]/estim[0];
printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\n", estim[0], std_dev[0], delta);
//  printf ("Result %d: %g +/- %g delta=%g\\n",NEPS, estim[0], std_dev[0], delta);
//  for (i=1; i<FUNCTIONS; ++i)
//    printf("Result %i:\\t%g +/- %g  \\tdelta=%g\\n", i, estim[i], std_dev[i],std_dev[i]/estim[i]);
  return(0);
}
    '''
    res = template.replace("<-DIMENSION->", str(len(str_region.split(","))/2))
    res = res.replace("<-ITERATIONS->", str(int(points)))
    res = res.replace("<-NTHREADS->",str(int(nthreads)))
    res = res.replace("<-REGION->",str_region)
    res = res.replace("<-VARS->",c_vars)
    
    res = res.replace("<-INTEGRAND->",c_expr)
    file = open(name+".c", 'w')
    file.write(res)
    file.close()
    
def GenerateCVars(g_vars):
    c_vars = ""
    region = list()
    var_cnt = 0
    # sorting for GenerateMCCodeForGraph to be sure
    # that all c_vars and regions are the same even if
    # g_vars disordered
    t_list = g_vars.keys()
    t_list.sort()
    for atom in t_list:
        reg = regex.match("^y\d+$", atom)
        if reg :
            c_vars = c_vars + "double %s = k[%s];\n" %(atom,var_cnt)
            var_cnt = var_cnt + 1
            region.append((0,1))
            continue
        
        reg = regex.match("^a_\d", atom)
        if reg :
            c_vars = c_vars + "double %s = k[%s];\n" %(atom,var_cnt)
            var_cnt = var_cnt + 1
            region.append((0,1))
            continue
        
        reg = regex.match("^ct_\d+_\d+$", atom)
        if reg :
            c_vars = c_vars + "double %s = k[%s];\n" %(atom,var_cnt)
            var_cnt = var_cnt + 1
            region.append((-1,1))
            continue
        
    str_region = ""
    for idx1 in [0,1]:
        for c_region in region:
            str_region = "%s, %s" %(str_region, str(c_region[idx1]))
    str_region = " { %s}" %str_region[1:]
    return (c_vars, str_region)
        

def GenerateMCCodeForTerm(name, g_expr, g_vars, space_dim, n_epsilon_series,
                          points, nthreads, debug=False):

    e = g_vars["e"]
    d = g_vars["d"]
    prog_names = list()
    t_expr = g_expr.subs(d == float(space_dim) - e)
    utils.print_time("GMCCFT: start", debug)
    for idxE in range(n_epsilon_series+1):
        utils.print_time("GMCCFT: eps^%s"%idxE, debug)
        cur_name = "%s_e%s" %(name,idxE)
        cur_expr = t_expr.subs(e == 0)
#        print swiginac.normal(cur_expr.subs(g_vars["y1"] == 0.99900000000001).subs(g_vars["y2"] == 0.99900000000001).subs(g_vars["ct_0_1"] == 0.999999))
        (c_vars, str_region) = GenerateCVars(g_vars)
        cur_expr.set_print_context('c')
        SavePThreadsMCCode(cur_name, cur_expr.str(), c_vars, str_region, points, nthreads)
        prog_names.append(cur_name)
        t_expr = t_expr.diff(e)/(idxE+1)
    utils.print_time("GMCCFT: end", debug)
    
    return prog_names 

def GenerateMCCodeForTermStrVars(name, prepared_eqs, space_dim, n_epsilon_series, 
                                 points, nthreads, debug=False, progress=None, 
                                 MCCodeGenerator=SavePThreadsMCCode):
#TODO: проверка что у всех членов одинаковые переменные.
    if progress <>  None:
        (progressbar,maxprogress) = progress
        cur_progress = progressbar.currval
    prog_names = list()
    expr_by_eps = dict()
    for i in range(n_epsilon_series+1):
        expr_by_eps[i] = list()
    c_vars = ""
    str_region = ""
    if progress <> None:
        step1 = float(maxprogress)/2./len(prepared_eqs)
    for idx in range(len(prepared_eqs)):
        (g_expr,g_vars, str_vars) = prepared_eqs[idx]
        e = g_vars["e"]
        d = g_vars["d"]
#        print g_expr
        t_expr = swiginac.subs(g_expr,d == float(space_dim) - e)
        
        for idxE in range(n_epsilon_series+1):
            cur_expr = t_expr.subs(e == 0)
            (c_vars, str_region) = GenerateCVars(g_vars)
            c_vars = "%s\n%s"%(c_vars,str_vars)
            cur_expr.set_print_context('c')
            c_expr = cur_expr.str()
            expr_by_eps[idxE].append((c_expr,c_vars,str_region))
            t_expr = t_expr.diff(e)/(idxE+1)
        if progress <> None:
            cur_progress = cur_progress + step1
            progressbar.update(cur_progress)

    if progress <> None:
        step2 = float(maxprogress)/2/len(expr_by_eps)        
    for idxE in expr_by_eps:
        
        #c_expr = expr_by_eps[idxE][0]
        for idxT in range(len(expr_by_eps[idxE])):
            cur_name = "%s_%s_e%s"%(name,idxT,idxE)
            c_expr = expr_by_eps[idxE][idxT][0]
            c_vars = expr_by_eps[idxE][idxT][1]
            str_region = expr_by_eps[idxE][idxT][2] 
            MCCodeGenerator(cur_name, c_expr, c_vars, str_region, points, nthreads)
            prog_names.append(cur_name)
        if progress <> None:
            cur_progress = cur_progress + step2
            progressbar.update(cur_progress)
    return prog_names  

def GenerateMCCodeForGraph(name, prepared_eqs, space_dim, n_epsilon_series, 
                           points, nthreads, debug=False):
#TODO: проверка что у всех членов одинаковые переменные.
    prog_names = list()
    expr_by_eps = dict()
    for i in range(n_epsilon_series+1):
        expr_by_eps[i] = list()
    c_vars = ""
    str_region = ""
    for idx in range(len(prepared_eqs)):
        (g_expr,g_vars) = prepared_eqs[idx]
        e = g_vars["e"]
        d = g_vars["d"]     
        t_expr = g_expr.subs(d == float(space_dim) - e)
        
        for idxE in range(n_epsilon_series+1):
            cur_expr = t_expr.subs(e == 0)
            (c_vars, str_region) = GenerateCVars(g_vars)
            cur_expr.set_print_context('c')
            c_expr = cur_expr.str()
            expr_by_eps[idxE].append(c_expr)
            t_expr = t_expr.diff(e)/(idxE+1)
            
    for idxE in expr_by_eps:
        cur_name = "MCO_%s_e%s"%(name,idxE)
        c_expr = expr_by_eps[idxE][0]
        for idxT in expr_by_eps[idxE][1:]:
            c_expr = "%s;\nf[0] = f[0] + %s" %(c_expr,idxT) 
        SavePThreadsMCCode(cur_name, c_expr, c_vars, str_region, points, nthreads)
        prog_names.append(cur_name)
        
    return prog_names

def GenerateMCCodeForGraphStrVars(name, prepared_eqs, space_dim, n_epsilon_series, 
                                  points, nthreads,debug=False, progress=None, 
                                  MCCodeGenerator=SavePThreadsMCCode):
    
    def JoinVars(prepared_eqs):
        g_vars_all=dict()
        str_vars_all=""
# TODO: Assumes that all definitions of one variable are the same        
        for eq in prepared_eqs:
            (g_expr,g_vars, str_vars)=eq
            for var in g_vars:
                if var not in g_vars_all:
                    g_vars_all[var] = g_vars[var]
            for str in str_vars.splitlines():
                reg = regex.search("(double .+) =", str)
                if reg: 
                    if reg.groups()[0] not in str_vars_all:
                        str_vars_all = "%s\n%s"%(str_vars_all,str)
        return(g_vars_all,str_vars_all)
        
    
#TODO: проверка что у всех членов одинаковые переменные.
    if progress <>  None:
        (progressbar,maxprogress) = progress
        cur_progress = progressbar.currval
    prog_names = list()
    expr_by_eps = dict()
    for i in range(n_epsilon_series+1):
        expr_by_eps[i] = list()
    c_vars = ""
    str_region = ""
    if progress <> None:
        step1 = float(maxprogress)/2./len(prepared_eqs)
    for idx in range(len(prepared_eqs)):
        (g_expr,g_vars, str_vars) = prepared_eqs[idx]
        #print "g_expr =",g_expr
#        print
        e = g_vars["e"]
        d = g_vars["d"]     
        t_expr = swiginac.subs(g_expr, d == float(space_dim) - e)
        
        for idxE in range(n_epsilon_series+1):
            cur_expr = t_expr.subs(e == 0)

            cur_expr.set_print_context('c')
            c_expr = cur_expr.str()
            expr_by_eps[idxE].append(c_expr)
            t_expr = t_expr.diff(e)/(idxE+1)
            
        if progress <> None:
            cur_progress = cur_progress + step1
            progressbar.update(cur_progress)


    (g_vars_joined,str_vars_joined) = JoinVars(prepared_eqs)
    (c_vars, str_region) = GenerateCVars(g_vars_joined)
    c_vars = "%s\n%s"%(c_vars,str_vars_joined)
#    print
#    print len(prepared_eqs)
#    print [expr_by_eps[i] for i in expr_by_eps]
#    print
        
    if progress <> None:
        step2 = float(maxprogress)/2/len(expr_by_eps)           
    for idxE in expr_by_eps:
        cur_name = "%s_e%s"%(name,idxE)
#        print "%s %s"%(idxE,expr_by_eps[idxE])
        c_expr = expr_by_eps[idxE][0]
#        print
#        print c_expr
        for idxT in expr_by_eps[idxE][1:]:
            c_expr = "%s;\nf[0] = f[0] + %s" %(c_expr,idxT)
#            print
#            print c_expr             
        MCCodeGenerator(cur_name, c_expr, c_vars, str_region, points, nthreads)
        prog_names.append(cur_name)
        
        if progress <> None:
            cur_progress = cur_progress + step2
            progressbar.update(cur_progress)
            
    return prog_names  

def GenerateCVarsF(vars_set):
    c_vars = ""
    vars = list(vars_set)
    for var in vars:
        c_vars = c_vars + "double %s = k[%s];\n"%(str(var),vars.index(var))
    print c_vars    
    
    str_region = " 0,"*len(vars)+" 1,"*len(vars)
    str_region = " { %s}" %str_region[:-1]
    return (c_vars,str_region)

def GenerateMCCodeForFeynman(name, expr_lst, space_dim, n_epsilon_series, 
                                  points, nthreads,debug=False, progress=None, 
                                  MCCodeGenerator=SavePThreadsMCCode):
    def JoinVarsF(expr_lst):
        vars = set()
        for expr in expr_lst:
            atoms = expr.atoms()
            for atom in atoms:
                print atom
                if regex.match('^(s|w)\d+', str(atom)):
                    print atom
                    vars = vars | set([atom,])
        return vars
    import sympy
#TODO: проверка что у всех членов одинаковые переменные.
    if progress <>  None:
        (progressbar,maxprogress) = progress
        cur_progress = progressbar.currval
    prog_names = list()
    expr_by_eps = dict()
    for i in range(n_epsilon_series+1):
        expr_by_eps[i] = list()
    if progress <> None:
        step1 = float(maxprogress)/2./len(expr_lst)
    e = sympy.var('e')
    for expr in expr_lst :
        t_expr = expr
        for idxE in range(n_epsilon_series+1):
            cur_expr = t_expr.subs(e, 0)

            #cur_expr.set_print_context('c')
            c_expr = sympy.ccode(cur_expr)
            expr_by_eps[idxE].append(c_expr)
            t_expr = t_expr.diff(e)/(idxE+1)
            
        if progress <> None:
            cur_progress = cur_progress + step1
            progressbar.update(cur_progress)


    vars_joined = JoinVarsF(expr_lst)
    print vars_joined
    (c_vars, str_region) = GenerateCVarsF(vars_joined)
#    print
#    print len(prepared_eqs)
#    print [expr_by_eps[i] for i in expr_by_eps]
#    print
        
    if progress <> None:
        step2 = float(maxprogress)/2/len(expr_by_eps)           
    for idxE in expr_by_eps:
        cur_name = "%s_e%s"%(name,idxE)
#        print "%s %s"%(idxE,expr_by_eps[idxE])
        c_expr = expr_by_eps[idxE][0]
#        print
#        print c_expr
        for idxT in expr_by_eps[idxE][1:]:
            c_expr = "%s;\nf[0] = f[0] + %s" %(c_expr,idxT)
#            print
#            print c_expr             
        MCCodeGenerator(cur_name, c_expr, c_vars, str_region, points, nthreads)
        prog_names.append(cur_name)
        
        if progress <> None:
            cur_progress = cur_progress + step2
            progressbar.update(cur_progress)
            
    return prog_names  

def GenerateMCCodeForFeynmanTerm(name, expr_lst, space_dim, n_epsilon_series, 
                                  points, nthreads,debug=False, progress=None, 
                                  MCCodeGenerator=SavePThreadsMCCode):
    def JoinVarsF(expr_lst):
        vars = set()
        for expr in expr_lst:
            atoms = expr.atoms()
            for atom in atoms:
                print atom
                if regex.match('^(s|w)\d+', str(atom)):
                    print atom
                    vars = vars | set([atom,])
        return vars
    import sympy
#TODO: проверка что у всех членов одинаковые переменные.
    if progress <>  None:
        (progressbar,maxprogress) = progress
        cur_progress = progressbar.currval
    prog_names = list()
    expr_by_eps = dict()
    for i in range(n_epsilon_series+1):
        expr_by_eps[i] = list()
    if progress <> None:
        step1 = float(maxprogress)/2./len(expr_lst)
    e = sympy.var('e')
    for expr in expr_lst :
        vars = JoinVarsF([expr,])
        (c_vars, str_region) = GenerateCVarsF(vars)

        t_expr = expr
        for idxE in range(n_epsilon_series+1):
            cur_expr = t_expr.subs(e, 0)

            #cur_expr.set_print_context('c')
            c_expr = sympy.ccode(cur_expr)
            expr_by_eps[idxE].append((c_expr,c_vars,str_region))
            t_expr = t_expr.diff(e)/(idxE+1)
            
        if progress <> None:
            cur_progress = cur_progress + step1
            progressbar.update(cur_progress)


    if progress <> None:
        step2 = float(maxprogress)/2/len(expr_by_eps)        
    for idxE in expr_by_eps:
        
        #c_expr = expr_by_eps[idxE][0]
        for idxT in range(len(expr_by_eps[idxE])):
            cur_name = "%s_%s_e%s"%(name,idxT,idxE)
            c_expr = expr_by_eps[idxE][idxT][0]
            c_vars = expr_by_eps[idxE][idxT][1]
            str_region = expr_by_eps[idxE][idxT][2] 
            MCCodeGenerator(cur_name, c_expr, c_vars, str_region, points, nthreads)
            prog_names.append(cur_name)
        if progress <> None:
            cur_progress = cur_progress + step2
            progressbar.update(cur_progress)

    return prog_names  


def CompileMCCode(prog_name, debug=False):
    import sys
#>>> process = subprocess.Popen(['./test', ], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#>>> process.wait()
#>>> process.communicate()
#gcc e12-e3-33--_m0_e0.c -lm -lpthread -lpvegas -o test
    utils.print_time("CMCCCode: start", debug)
    code_name="%s.c"%prog_name
    process = subprocess.Popen(["rm", "-f", prog_name], shell=False, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = process.wait()
    (std_out, std_err) = process.communicate()
    utils.print_time("CMCCCode: ",debug)    
    utils.print_debug( "Compiling %s ... " %prog_name, debug)
    sys.stdout.flush()
    process = subprocess.Popen(["gcc", code_name, "-lm", "-lpthread", 
                                "-lpvegas","-O2", "-o", prog_name], shell=False, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = process.wait()
    (std_out, std_err) = process.communicate()
    
    if exit_code <> 0 :
        utils.print_debug( "\t\t\t\t\t\t\tFAILED",debug)
        utils.print_debug( std_err,debug)
        res = None
    else: 
        if len(std_err) == 0:
            utils.print_debug( "\t\t\t\t\t\t\tOK",debug)
            res = True
        else:
            utils.print_debug( "\t\t\t\t\t\t\tCHECK", debug)
            print std_err
            res = True
    utils.print_time("CMCCCode: end",debug)
    return True


def ExecMCCode(prog_name, points=10000, threads=2,debug=False, calc_delta=None):
    import sys
#>>> process = subprocess.Popen(['./test', ], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#>>> process.wait()
#>>> process.communicate()
#gcc e12-e3-33--_m0_e0.c -lm -lpthread -lpvegas -o test
    MAXPOINTS=10**9
    if points >= MAXPOINTS:
        iterations = 2*int(points/MAXPOINTS)
        points = MAXPOINTS
    else:
        iterations = 2
    utils.print_time("EMCCCode: start", debug)
    utils.print_debug("Executing %s points=%s threads=%s ... " %(prog_name, points, threads) , debug)
    sys.stdout.flush()
    arg_lst=["./%s"%prog_name, "%s"%points, "%s"%threads]
    arg_lst.append(str(iterations))
    if calc_delta<>None:
        arg_lst.append("%s"%calc_delta)
    
    utils.print_debug("args = %s"%arg_lst,debug)
    process = subprocess.Popen(arg_lst, shell=False, 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    exit_code = process.wait()
    (std_out,std_err) = process.communicate()
    if exit_code <> 0 :
        utils.print_debug("FAILED",debug)
        utils.print_debug(std_err,debug)
        result = None
    else: 
        if len(std_err) == 0:
            utils.print_debug( "OK ", debug)
#Result 0:\t0.00599252 +/- 0.000130637  \tdelta=0.0217999\n
            res = None
            err = None
            deltA = None
            for line in std_out.splitlines():
                reg = regex.match("^result = (.+)$", line)
                if reg:
                    if 'nan' not in reg.groups()[0]:
                        res = float(reg.groups()[0])
                    else:
                        utils.print_debug("res = %s"%reg.groups()[0],debug) 
                        res = 0.
                reg = regex.match("^std_dev = (.+)$", line)
                if reg:
                    if 'nan' not in reg.groups()[0]:
                        err = float(reg.groups()[0])
                    else:
                        utils.print_debug("err = %s"%reg.groups()[0],debug)
                        err = 10000000.
                reg = regex.match("^delta = (.+)$", line)
                if reg:
                    if 'nan' not in reg.groups()[0]:
                        deltA = float(reg.groups()[0])
                    else:
                        utils.print_debug("delta = %s"%reg.groups()[0],debug)
                        deltA = 10000000.
            if res <> None and err <> None and deltA <> None:
                utils.print_debug("res = %s, err = %s, delta = %s" %(res, err, deltA),debug)
                result = (res, err, deltA)
            else:
                utils.print_debug("CHECK",debug)
                utils.print_debug(std_out,debug)
                result = None
        else:
            utils.print_debug( "CHECK", debug)
            utils.print_debug( std_err, debug)
            result = None
            
    utils.print_time("EMCCCode: exec end",debug)
    return result

def CalculateEpsilonSeries(prog_names, build=False, points=10000, threads=2, debug=False, progress = None, calc_delta=None):
    res_by_eps = dict()
    if progress <>  None:
        (progressbar,maxprogress) = progress
        step = float(maxprogress)/len(prog_names)
        cur_progress = progressbar.currval

    for prog in prog_names:
        if build == True:
            build_res = CompileMCCode(prog,debug)
            if build_res == None:
                raise Exception, "CompileMCCode failed to build %s" %prog
        exec_res = ExecMCCode(prog, points=points, threads=threads, debug=debug, calc_delta=calc_delta)
        if exec_res == None:
            raise ValueError , "ExecMCCode function returns None: prog = %s" %prog
        (res, dev, deltA) = exec_res
        reg = regex.search("_e(\d+)$",prog)
        if reg:
            eps = int(reg.groups()[0])
        else:
            raise ValueError, "Can't determine eps power for %s" %prog
        if eps in res_by_eps:
            cur = res_by_eps[eps]
            res_by_eps[eps] = (cur[0]+res, cur[1]+dev)
        else:
            res_by_eps[eps] = (res, dev)
        if progress <>  None:
            cur_progress = cur_progress + step
            progressbar.update(cur_progress)
    return res_by_eps
