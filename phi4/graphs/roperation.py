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
#        print "%s : %s"%(dim,sub)
        if dim>=0:
            sub._strechvar = "a_%s"%(sub.asLinesIdxStr())
            sub._diffcnt=dim+1
            extatoms=FindExternalAtoms(sub)
            setStrech(sub, extatoms)

def find_strech_atoms(expr):
    atoms = expr.atoms(sympy.core.symbol.Symbol)
    atomlst = list()
    for atom in atoms:
        reg1 = regex.match("^a_\d*.*$", str(atom))
        reg2 = regex.match("^u_\d*.*$", str(atom))
        if reg1 or reg2:
            atomlst.append(atom)
#    print atomlst
    return set(atomlst)


def expr(graph, model):
    if "_subgraphs_m" in graph.__dict__:
        subgraphs=graph._subgraphs_m
    else:
        subgraphs=graph._subgraphs
    res=graph.expr(model)
    for sub in subgraphs:
        if "_strechvar" in sub.__dict__:
            
            var=sympy.var(sub._strechvar)
            res = res.diff(var, int(sub._diffcnt))
            if sub._diffcnt>1:
                res=res*(1-var)**(sub._diffcnt-1)/sympy.factorial(sub._diffcnt-1)
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
        if model.space_dim -3 - (graph.NLoops()-3)<0:
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
                sympy.var('st_%s_%s'%(i,j))
                jakob=jakob*2

                if i == 0:
                    res['q%sOq%s'%(i,j)]=eval('ct_%s_%s'%(i,j))
                elif  i == 1:
                    res['q%sOq%s'%(i,j)]=eval('ct_0_{0}*ct_0_{1}+st_0_{0}*st_0_{1}*ct_{0}_{1}'.format(i,j))
                elif  i == 2:
                    res['q%sOq%s'%(i,j)]=eval('ct_0_{0}*ct_0_{1}+st_0_{0}*st_0_{1}*(ct_1_{0}*ct_1_{1}+st_1_{0}*st_1_{1}*ct_{0}_{1})'.format(i,j))
                else:
                    raise NotImplementedError, "nloops>4"
        return jakob, res


def export_subs_vars_pv(subs_vars, strechs):
    def sort_vars(var_list):
        c=[]
        s=[]
        q=[]
        a=[]
        u=[]
        for var in var_list:
            if regex.match('^c.*',var):
                c.append(var)
            elif regex.match('^s.*',var):
                s.append(var)
            elif regex.match('^q.*',var):
                q.append(var)
            elif regex.match('^a.*',var):
                a.append(var)
            elif regex.match('^u.*',var):
                u.append(var)        
        c.sort()
        s.sort()
        q.sort()
        a.sort()
        u.sort()
        return u+c+s+q+a
    res=""
    atomset=set()
    for expr in subs_vars.values():
        atomset=atomset|expr.atoms(sympy.core.symbol.Symbol)
    cnt=0
    for atom in atomset|strechs:
        if regex.match("^y\d*$",str(atom)) or regex.match("^z_\d+_\d+$",str(atom)) or regex.match("^a_\d+.*$",str(atom))or regex.match("^u_\d+.*$",str(atom)):
            res=res+"double %s = k[%s];\n"%(atom,cnt)
            cnt+=1
    region=("0.,"*cnt+"1.,"*cnt)[:-1]
    res="#define DIMENSION %s\n"%cnt+"#define FUNCTIONS 1\n"+"#define ITERATIONS 5\n" + "#define NTHREADS 2\n" +"#define NEPS 0\n"+"#define NITER 2\n" +  "double reg_initial[2*DIMENSION]={%s};\nvoid func (double k[DIMENSION], double f[FUNCTIONS])\n {\n"%region+res

    for var in sort_vars(subs_vars.keys()):
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

def core_pv_code(integrand):
    a1="""#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#define gamma tgamma
"""
    a1=a1+integrand
    a1=a1+ """ }



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
"""
    return a1
