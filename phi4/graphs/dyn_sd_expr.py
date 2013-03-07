#!/usr/bin/python
# -*- coding: utf8


import sys
import re

import graph_state
import polynomial.sd_lib as sd_lib
import polynomial

import subgraphs
from dummy_model import _phi3_dyn, _phi4_dyn

import dynamics


def splitUA(varSet):
    u = list()
    a = list()
    for var in varSet:
        if isinstance(var, str) and re.match('^a.*', var):
            a.append(var)
        else:
            u.append(var)
    return set(u), set(a)


def deltaArg(varSet):
    return polynomial.poly(map(lambda x: (1, [x]), varSet))


model = _phi4_dyn("phi4_dyn_test")

filename = sys.argv[1]

exec ('import %s as data' % filename[:-3])

print data.graphName

gs = graph_state.GraphState.fromStr(data.graphName)
tVersion = data.tVersion

dG = dynamics.DynGraph(gs)
dG.FindSubgraphs(model)
subgraphs.RemoveTadpoles(dG)
Components = dynamics.generateCDET(dG, tVersion, model=model)
print str(gs)
print tVersion
#print "C = %s\nD = %s\nE = %s\nT = %s\n" % tuple(Components)
C, D, E, T = Components
#d=4-2*e


expr = C * D * E * T
#print expr

variables = expr.getVarsIndexes()
print "variables: ", variables
uVars, aVars = splitUA(variables)
delta_arg = deltaArg(uVars)

codeTemplate = """
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#include <time.h>
#define gamma tgamma
#define DIMENSION {dim}
#define FUNCTIONS 1
#define ITERATIONS 5
#define NTHREADS 2
#define NEPS 0
#define NITER 2
double reg_initial[2*DIMENSION]={hypercube};

void func (double k[DIMENSION], double f[FUNCTIONS])
 {{
  {vars}
  f[0]=0.;
  {expr}
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

  vegas(reg, DIMENSION, func,
        0, npoints/10, 5, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
  vegas(reg, DIMENSION, func,
        2, npoints , niter, NPRN_INPUT | NPRN_RESULT,
        FUNCTIONS, 0, nthreads,
        estim, std_dev, chi2a);
    int rank=0;

    if(rank==0) {{
        end = clock();
        elapsed = ((double) (end - start)) / CLOCKS_PER_SEC;
        double delta= std_dev[0]/estim[0];
        printf ("result = %20.18g\\nstd_dev = %20.18g\\ndelta = %20.18g\\ntime = %20.10g\\n", estim[0], std_dev[0], delta, elapsed);
    }}
    return(0);
}}
"""

print
print "-------------------"
sectorCount = -1
for sector, aOps in data.sectors:
    sectorCount += 1
    sectorFileName = "dyn_sectors/%s_N%s.c" % (filename[:-3], sectorCount)

    sectorExpr = [sd_lib.sectorDiagram(expr, sector, delta_arg=delta_arg)]

    for aOp in aOps:
        sectorExpr = aOp(sectorExpr)
    sectorExpr = map(lambda x: x.simplify(), sectorExpr)
    check = dynamics.checkDecomposition(sectorExpr)
    print sector, check
    if "bad" in check:
        print
        print polynomial.formatter.format(sectorExpr, polynomial.formatter.CPP)
        print

    sectorVariables = set()
    for expr_ in sectorExpr:
        sectorVariables = sectorVariables | set(polynomial.formatter.formatVarIndexes(expr_, polynomial.formatter.CPP))

    nIntegrations = len(sectorVariables)
    hyperCube = '{' + ",".join(['0', ] * nIntegrations) + "," + ",".join(['1', ] * nIntegrations) + "}"
    varIdx = 0
    strVars = ""
    for var in sectorVariables:
        strVars += "   double %s = k[%s];\n" % (var, varIdx)
        varIdx += 1
    strExpr = ""
    for expr_ in sectorExpr:
        coreExpr, epsDict = expr_.epsExpansion(0)
        if len(epsDict[0]) == 1 : ### !!!!!
            strExpr += "   f[0] += %s * %s;" % (polynomial.formatter.format(coreExpr, polynomial.formatter.CPP),
                                                polynomial.formatter.format(epsDict[0][0], polynomial.formatter.CPP))

        else:
            raise ValueError, "epsDict = %s" % epsDict
    f = open(sectorFileName, "w")
    f.write(codeTemplate.format(
        vars=strVars,
        hypercube=hyperCube,
        dim=nIntegrations,
        expr=strExpr
    ))
    f.close()

