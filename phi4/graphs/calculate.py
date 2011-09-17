#!/usr/bin/python
# -*- coding:utf8
import os
import roperation
import sympy
import utils

def save(name, graph, model, overwrite=True):
    dirname = '%s/%s/'%(model.workdir,name)
    try:
        os.mkdir(dirname)
    except:
        if overwrite:
            file_list = os.listdir(dirname)
            for file in file_list:
                os.remove(dirname+file)

    jakob,subsvars = roperation.subs_vars(graph)
    cnt=0
    d,e=sympy.var('d e')
    for g in model.dTau(graph):
        roperation.strechMoments(g, model)
        print cnt, g
        det=roperation.det(g, model)
        expr=(utils.norm(graph.NLoops(),d)*jakob*det*roperation.AvgByExtDir(roperation.expr(g,model))).subs(d, model.space_dim-e)
        strechs=roperation.find_strech_atoms(expr)
        eps_cnt=0
        if "_nloops_orig" in graph.__dict__:
            _nloops_orig=graph._nloops_orig
        else:
            _nloops_orig=graph.NLoops()

        for _expr in utils.series_lst(expr,e,model.target-_nloops_orig):
            integrand=roperation.export_subs_vars_pv(subsvars,strechs)
            integrand+= "\nf[0]=0.;\n"
            integrand+= "f[0]+=%s;\n"%sympy.printing.ccode(_expr)
            f=open('%s/%s_E%s_%s.c'%(dirname,name,eps_cnt,cnt),'w')
            f.write(core_pv_code(integrand))
            f.close()
            eps_cnt+=1
        cnt+=1  
    


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
