#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>

#define DIMENSION 2
#define NITER 2
#define FUNCTIONS 1
#define ITERATIONS 10000
#define NTHREADS 4
#define NEPS 0
#ifndef PI
#define PI     3.14159265358979323846
#endif
double reg[2*DIMENSION]= {0,0,1,1};
void func (double k[DIMENSION], double f[FUNCTIONS]) {
//double Pi=PI;
double u=k[0];
double t=k[1];
f[0]=t*(1/((1.0 + t*(0.5 - 0.5*u)*(1.0 - 0.5*t*u))*(1.0 + t*(0.5 - 0.5*u)*(1.0 - 0.5*t*u))*(1.0 + t*(0.5 - 0.5*u)*(1.0 - 0.5*t*u)))*(1.0 - 0.5*t*u) + 1/((t + (0.5 - 0.5*t*u)*(1.0 - 0.5*u))*(t + (0.5 - 0.5*t*u)*(1.0 - 0.5*u))*(t + (0.5 - 0.5*t*u)*(1.0 - 0.5*u)))*(1.0 - 0.5*u));  }




int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{
  int i;
  long long npoints;
  int nthreads;
  int niter;
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
//  //  for (i=1; i<FUNCTIONS; ++i)
//  //    printf("Result %i:\\t%g +/- %g  \\tdelta=%g\\n", i, estim[i], std_dev[i],std_dev[i]/estim[i]);
//    return(0);
//    }
}
