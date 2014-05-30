
#include <math.h>
#include "dim.h"


double func0_t_0(double k[DIMENSION])
{
// sector 0
   double u4 = k[0];
   double u3 = k[1];

double coreExpr;
double f=0;
   coreExpr = ((u3))*((u4))*(pow(1+u3+u3*u4, -2.0))*(pow(1+u4+u3*u4, -2.0));
   f += coreExpr * -1.0;

return f;
}



double func_t_0(double k[DIMENSION])
{
double f=0;
f+=func0_t_0(k);

return f;
}

