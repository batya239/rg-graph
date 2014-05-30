
#include <math.h>
#include "dim.h"


double func0_t_0(double k[DIMENSION])
{
// sector 0
   double u5 = k[0];
   double u4 = k[1];
   double u6 = k[2];
   double u3 = k[3];

double coreExpr;
double f=0;
   coreExpr = (pow(1+u5+u5*u6+u3*u5*u6+u4*u5*u6, -3.0))*((u4))*(pow(u5, 2.0))*(pow(u6, 2))*(pow(1+u4*u6+u3*u4*u5*u6+u3+u3*u5*u6+u3*u4*u5*pow(u6, 2)+u3*u6+u4, -2.0))*((1+u3+u3*u6+u3*u5*u6));
   f += coreExpr * -2.0;

return f;
}

double func1_t_0(double k[DIMENSION])
{
// sector 1
   double u5 = k[0];
   double u6 = k[1];
   double u3 = k[2];
   double u2 = k[3];

double coreExpr;
double f=0;
   coreExpr = ((u3+u5*u6+u3*u6+u3*u5*u6))*(pow(1+u2*u5*u6+u2*u5+u2+u2*u3, -3.0))*(pow(u2, 2.0))*(pow(1+u2*u3*u6+u6+u3+u2*u5*u6+u3*u6+u2*u3+u2*u3*u5*u6, -2.0));
   f += coreExpr * -2.0;

return f;
}

double func2_t_0(double k[DIMENSION])
{
// sector 2
   double u5 = k[0];
   double u4 = k[1];
   double u6 = k[2];
   double u3 = k[3];

double coreExpr;
double f=0;
   coreExpr = ((1+u6+u5*u6+u3*u5*u6))*((u4))*(pow(u3, 2.0))*(pow(1+u5*u6+u4*u6+u3*u4+u6+u3*u5*u6+u3*u4*u6+u4, -2.0))*(pow(1+u3+u3*u5+u3*u5*u6+u3*u4, -3.0));
   f += coreExpr * -2.0;

return f;
}

double func3_t_0(double k[DIMENSION])
{
// sector 3
   double u5 = k[0];
   double u4 = k[1];
   double u6 = k[2];
   double u3 = k[3];

double coreExpr;
double f=0;
   coreExpr = (pow(u4, 2.0))*((u3*u4*u5*u6+u3+u5*u6+u3*u6))*(pow(1+u4*u5*u6+u4+u4*u5+u3*u4, -3.0))*(pow(1+u5*u6+u3*u4+u3*u4*u5*u6+u3+u3*u4*u6+u3*u6+u6, -2.0));
   f += coreExpr * -2.0;

return f;
}

double func4_t_0(double k[DIMENSION])
{
// sector 4
   double u5 = k[0];
   double u4 = k[1];
   double u6 = k[2];
   double u3 = k[3];

double coreExpr;
double f=0;
   coreExpr = (pow(u3*u4*u5+1+u4*u6+u3*pow(u4, 2)*u5*u6+u6+u3+u3*u4*u6+u3*u4*u5*u6, -2.0))*(pow(u4, 2))*(pow(u5, 2.0))*(pow(1+u3*u4*u5+u4*u5*u6+u4*u5+u5, -3.0))*((u3*u4*u6+u3*u4*u5*u6+u3+u6));
   f += coreExpr * -2.0;

return f;
}

double func5_t_0(double k[DIMENSION])
{
// sector 5
   double u5 = k[0];
   double u4 = k[1];
   double u6 = k[2];
   double u3 = k[3];

double coreExpr;
double f=0;
   coreExpr = (pow(1+pow(u3, 2)*u4*u5*u6+u6+u3*u5*u6+u3*u4*u6+u3*u4*u5+u3*u6+u4, -2.0))*((1+u6+u3*u6+u3*u5*u6))*(pow(u3, 2))*((u4))*(pow(u5, 2.0))*(pow(1+u3*u4*u5+u3*u5+u3*u5*u6+u5, -3.0));
   f += coreExpr * -2.0;

return f;
}



double func_t_0(double k[DIMENSION])
{
double f=0;
f+=func0_t_0(k);
f+=func1_t_0(k);
f+=func2_t_0(k);
f+=func3_t_0(k);
f+=func4_t_0(k);
f+=func5_t_0(k);

return f;
}

