#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <omp.h>
#include "cuba.h"

//#define OPENMP_PARALLEL

/*-----Definitions that may vary from function to function-----*/
#ifdef OPENMP_PARALLEL
#include "integrate_parallel.h"
#endif

#ifndef OPENMP_PARALLEL
#include "integrate.h"
#endif

/*-------------------------------------------------------------*/

/*-----Definitions that are constant for every function--------*/

#define NCOMP 1
#define EPSREL 1e-7
#define EPSABS 1e-12
#define LAST 4
#define SEED 0
#define MINEVAL 0
#define MAXEVAL 50000

#define NSTART 1000
#define NINCREASE 500
#define NBATCH 10000
#define GRIDNO 0
#define STATEFILE NULL

/*-------------------------------------------------------------*/

int main()
{
    int verbose, comp, neval, fail;
    double integral[NCOMP], error[NCOMP], prob[NCOMP];
    const char *env = getenv("CUBAVERBOSE");
    FILE *fp;
    verbose = 2;
    if (env)
        verbose = atoi(env);

#ifdef OPENMP_PARALLEL

    int i, semaphore = 0;

#pragma omp parallel for default(none)\
    shared(verbose, semaphore)\
    private(i, neval, fail, integral, error, prob, comp)

    for (i = 0; i < 4; i++)
    {
        Vegas(NDIM, NCOMP, Integrand, &i, EPSREL, EPSABS, verbose, SEED,
                MINEVAL, MAXEVAL, NSTART, NINCREASE, NBATCH, GRIDNO, STATEFILE,
                &neval, &fail, integral, error, prob);

        while (1)
        {
            if (semaphore == omp_get_thread_num())
            {
                semaphore = -1;
                printf("THREAD #%d VEGAS RESULT:\tneval %d\tfail %d\n", omp_get_thread_num(), neval, fail);
                for (comp = 0; comp < NCOMP; ++comp)
                printf("VEGAS RESULT:\t%.8f +- %.8f\tp = %.3f\n",
                        integral[comp], error[comp], prob[comp]);

                printf("\n");
                semaphore = omp_get_thread_num() + 1;
                break;
            }
        }
    }
#endif

#ifndef OPENMP_PARALLEL

    fp = fopen("out.txt", "a");

    Vegas(NDIM, NCOMP, Integrand, NULL, EPSREL, EPSABS, verbose, SEED, MINEVAL,
            MAXEVAL, NSTART, NINCREASE, NBATCH, GRIDNO, STATEFILE, &neval,
            &fail, integral, error, prob);

    //printf("VEGAS RESULT:\tneval %d\tfail %d\n", neval, fail);
    for (comp = 0; comp < NCOMP; ++comp)
        printf("%.8f %.8f", integral[comp], error[comp]);

//    printf("\n");

    for (comp = 0; comp < NCOMP; ++comp)
            fprintf(fp, "(%.8f +- %.8f), x^2-prob = %.8f\n", integral[comp], error[comp], prob[comp]);
    fclose(fp);

#endif

    return 0;
}

