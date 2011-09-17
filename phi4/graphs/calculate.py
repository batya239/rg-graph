#!/usr/bin/python
# -*- coding:utf8

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
