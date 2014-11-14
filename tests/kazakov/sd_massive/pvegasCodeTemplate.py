corePvegasCodeTemplate = """
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#include <time.h>
#define gamma tgamma
#define FUNCTIONS 1
#define ITERATIONS 5
#define NTHREADS 2
#define NEPS 0
#define NITER 2

{includes}
#ifdef MPI
#include <mpi.h>
#endif

double reg_initial[2*DIMENSION]={{{region}}};

void func (double k[DIMENSION], double f[FUNCTIONS])
 {{
  f[0]=0.;
  
  {functions}

 }}



int t_gfsr_k;
unsigned int t_gfsr_m[SR_P];
double gfsr_norm;


int main(int argc, char **argv)
{{
  int i;
  long long npoints;
  int nthreads;
  int niter;
  double region_delta;
  double reg[2*DIMENSION];
  int idx;
  if(argc >= 2)
    {{
      npoints = atoll(argv[1]);

    }}
  else
    {{
      npoints = ITERATIONS;
    }}

  if(argc >= 3)
    {{
      nthreads = atoi(argv[2]);

    }}
  else
    {{
      nthreads = NTHREADS;
    }}

   if(argc >= 5)
    {{
      region_delta = atof(argv[4]);

    }}
  else
    {{
      region_delta = 0.;
    }}

  if(argc >= 4)
    {{
      niter = atoi(argv[3]);

    }}
  else
    {{
      niter = NITER;
    }}

    for(idx=0; idx<2*DIMENSION; idx++)
      {{
         if(idx<DIMENSION)
           {{
             reg[idx] = reg_initial[idx]+region_delta;
           }}
         else
           {{
             reg[idx] = reg_initial[idx]-region_delta;
           }}
      }}

  double estim[FUNCTIONS];   /* estimators for integrals                     */
  double std_dev[FUNCTIONS]; /* standard deviations                          */
  double chi2a[FUNCTIONS];   /* chi^2/n                                      */
    clock_t start, end;
    double elapsed;
    start = clock();

#ifdef MPI
MPI_Init(&argv, &argc);
#endif

  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
    int rank=0;

#ifdef MPI
MPI_Comm_rank(MPI_COMM_WORLD,&rank);
MPI_Finalize();
#endif

    if(rank==0) {{
        end = clock();
        elapsed = ((double) (end - start)) / CLOCKS_PER_SEC;
        double delta= std_dev[0]/estim[0];
        printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\ntime = %20.10g\\n", estim[0], std_dev[0], delta, elapsed);
    }}
    return(0);
}}
"""

