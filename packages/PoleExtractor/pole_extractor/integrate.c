#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "cuba.h"


/*-----Definitions that may vary from function to function-----*/

#include "integrate.h"

/*-------------------------------------------------------------*/

/*-----Definitions that are constant for every function--------*/


#define NCOMP 1
#define NVEC 1
#define EPSREL 1e-3
#define EPSABS 1e-12
#define LAST 4
#define SEED 0
#define MINEVAL 0
#define MAXEVAL 1E8

#define NSTART 1000
#define NINCREASE 500
#define NBATCH 10000
#define GRIDNO 0
#define STATEFILE NULL

//#define KEY1 47
//#define KEY2 1
//#define KEY3 1
//#define MAXPASS 5
//#define BORDER 0.
//#define MAXCHISQ 10.
//#define MINDEVIATION .25
//#define NGIVEN 0
//#define LDXGIVEN NDIM
//#define NEXTRA 0


/*-------------------------------------------------------------*/

int main()
{
    int verbose, comp, neval, fail;
    double integral[NCOMP], error[NCOMP], prob[NCOMP];
    const char *env = getenv("CUBAVERBOSE");
    verbose = 2;
    if (env)
        verbose = atoi(env);

    Vegas(NDIM, NCOMP, Integrand, NULL, NVEC, EPSREL, EPSABS, verbose, SEED,
          MINEVAL, MAXEVAL, NSTART, NINCREASE, NBATCH, GRIDNO, STATEFILE,
          &neval, &fail, integral, error, prob);


    for (comp = 0; comp < NCOMP; ++comp)
        printf("%.8f %.8f", integral[comp], error[comp]);

    return 0;
}

