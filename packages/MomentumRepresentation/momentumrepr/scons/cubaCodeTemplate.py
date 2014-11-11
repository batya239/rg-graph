coreCubaCodeTemplate = """
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include "{cuba_path}"

{includes}

static int Integrand(const int *ndim, const double xx[],
  const int *ncomp, double ff[], void *userdata)
{{
#define f ff       // FIXME?
  f[0] = 0.;   // FIXME?
  {functions}
  return 0;
}}

/*********************************************************************/

#define NDIM DIMENSION 
#define NCOMP 1
#define USERDATA NULL
#define LAST 4
#define SEED 0
#define MINEVAL 0

#define SPIN NULL
#define NVEC 1
#define NSTART 1000
#define NINCREASE 500
#define NBATCH 1000
#define GRIDNO 0
#define STATEFILE "cuba.state"
#define RETAIN_STATE 1 << 3
#define Pi 3.1415926535897932384626433832795028841971

#define NNEW 1000
#define FLATNESS 25.

#define KEY1 47
#define KEY2 1
#define KEY3 1
#define MAXPASS 5
#define BORDER 0.
#define MAXCHISQ 10.
#define MINDEVIATION .25
#define NGIVEN 0
#define LDXGIVEN NDIM
#define NEXTRA 0

#define KEY 0

int main(int argc, char* argv[])
{{
  if (argc < 5) {{
      printf("Usage: %s <method> <maxPoints> <EpsRel> <EpsAbs>\\n \
       where 'method' is either '1' for 'suave' or '2' for 'divonne',\\n \
       'EpsRel' and 'EpsAbs' should look like '1e-6'\\n \
       Example: ./cuba.run 2 10000 1e-4 1e-12 \\n", argv[0]);
      return 1;
  }}
 

  int METHOD = atoi(argv[1]);
  #define MAXEVAL atoll(argv[2])
  #define EPSREL atof(argv[3])
  #define EPSABS atof(argv[4])
  
  int verbose, comp, nregions, fail;
  long long int neval;
  double integral[NCOMP], error[NCOMP], prob[NCOMP];

  const char *env = getenv("CUBAVERBOSE");
  verbose = 2;
  if( env ) verbose = atoi(env);

if (METHOD == 0) {{
  printf("-------------------- Vegas test --------------------\\n");
  void *spin = NULL;
  llVegas(NDIM, NCOMP, Integrand, USERDATA, NVEC,
    EPSREL, EPSABS, verbose | RETAIN_STATE, SEED,
    MINEVAL, MAXEVAL, NSTART, NINCREASE, NBATCH,
    GRIDNO, STATEFILE, &spin,
    &neval, &fail, integral, error, prob);
  printf("VEGAS RESULT:\tneval %d\tfail %d\\n",
    neval, fail);
  for( comp = 0; comp < NCOMP; ++comp )
    printf("VEGAS RESULT:\t%.14f +- %.14f\tp = %.3f\\n",
      integral[comp], error[comp], prob[comp]);
}}
else if (METHOD == 1) {{
  printf("\\n-------------------- Suave test --------------------\\n");

  llSuave(NDIM, NCOMP, Integrand, USERDATA, NVEC,
    EPSREL, EPSABS, verbose | LAST | RETAIN_STATE, SEED,
    MINEVAL, MAXEVAL, NNEW, FLATNESS, STATEFILE, SPIN,
    &nregions, &neval, &fail, integral, error, prob);

  printf("SUAVE RESULT:\tnregions %d\tneval %d\tfail %d\\n",
    nregions, neval, fail);
  for( comp = 0; comp < NCOMP; ++comp )
    printf("SUAVE RESULT:\t%.14f +- %.14f\tp = %.3f\\n",
      integral[comp], error[comp], prob[comp]);
}}
else if (METHOD == 2) {{
  printf("\\n------------------- Divonne test -------------------\\n");

  llDivonne(NDIM, NCOMP, Integrand, USERDATA, NVEC,
    EPSREL, EPSABS, verbose | RETAIN_STATE, SEED,
    MINEVAL, MAXEVAL, KEY1, KEY2, KEY3, MAXPASS,
    BORDER, MAXCHISQ, MINDEVIATION,
    NGIVEN, LDXGIVEN, NULL, NEXTRA, NULL, STATEFILE, SPIN,
    &nregions, &neval, &fail, integral, error, prob);

  printf("DIVONNE RESULT:\tnregions %d\tneval %d\tfail %d\\n",
    nregions, neval, fail);
  for( comp = 0; comp < NCOMP; ++comp )
    printf("DIVONNE RESULT:\t%.14f +- %.14f\tp = %.3f\\n",
      integral[comp], error[comp], prob[comp]);
}}
else if (METHOD == 3) {{
  printf("\\n-------------------- Cuhre test --------------------\\n");

  llCuhre(NDIM, NCOMP, Integrand, USERDATA, NVEC,
    EPSREL, EPSABS, verbose | LAST | RETAIN_STATE,
    MINEVAL, MAXEVAL, KEY, STATEFILE, SPIN,
    &nregions, &neval, &fail, integral, error, prob);

  printf("CUHRE RESULT:\tnregions %d\tneval %d\tfail %d\\n",
    nregions, neval, fail);
  for( comp = 0; comp < NCOMP; ++comp )
    printf("CUHRE RESULT:\t%.14f +- %.14f\tp = %.3f\\n",
      integral[comp], error[comp], prob[comp]);
}}
  return 0;
}}
"""

