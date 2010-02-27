#!/usr/bin/python
# -*- coding:utf8
import sys
import rggraph_static as rggrf


if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    filename = "moment"

from phi3 import *


print phi3.name

base_name = "fns_custom"
TARGET = 4
NLOOPS = 3
print "NLOOPS = " , NLOOPS
n_epsilon_series = TARGET - NLOOPS
NPOINTS = 10000
NTHREADS = 2 
SPACE_DIM = 6.
prepared_eqs = []

var('q1 q2 q3 q4 q1xq2 q1xq3 q1xq4 q2xq3 q2xq4 q3xq4 a b')
#tmp=((1/(q1**2*a*a+q2**2+2*q1xq2*a+1)).diff(a)*
#     (1/((q1**2*a*a*b*b+q3**2+2*q1xq3*a*b+1)*(q2**2*b*b+q3**2-2*q2xq3*b+1))).diff(b)+
#     (1/(q1**2*a*a+q3**2+2*q1xq3*a+1)).diff(a)*
#     (1/((q1**2*a*a*b*b+q2**2+2*q1xq2*a*b+1)*(q3**2*b*b+q2**2-2*q2xq3*b+1))).diff(b)).diff(a).diff(a)*(1-a)**2
#k2term =   rggrf.roperation.Factorized(1/(q1**2+1)**5/(q2**2+1)/(q3**2+1),tmp)

#tmp = (1/(q1**2*a*a+q2**2+2*q1xq2*a+1)).diff(a)*(1/(q2**2*b*b+q3**2+2*q2xq3*b+1)).diff(b)
#k2term =   rggrf.roperation.Factorized(1/(q1**2+1)/(q2**2+1)/(q3**2+1),tmp)

#
### 4loop
#

tmp =(1/(a*a*q1*q1+q2*q2+2*q1xq2*a+1)/(a*a*q1*q1+q3*q3+2*q1xq3*a+1)/
      (q2*q2+q4*q4+2*q2xq4+1)/(q3*q3+q4*q4+2*q3xq4+1)*
         (1/(a**2*q1**2+q2**2+q3**2+q4**2+2*q1xq2*a+
             2*q1xq3*a+2*q1xq4*a+2*q2xq3+2*q2xq4+2*q3xq4+1)
         ).diff(a)+
         (1/(a*a*q1*q1+q2*q2+2*q1xq2*a+1)).diff(a)*
             (1/(a**2*b**2*q1**2+b**2*q2**2+q3**2+q4**2+2*q1xq2*a*b*b+
             2*q1xq3*a*b+2*q1xq4*a*b+2*q2xq3*b+2*q2xq4*b+2*q3xq4+1)/
             (a*a*b*b*q1*q1+q3*q3+2*q1xq3*a*b+1)/(b*b*q2*q2+q4*q4+2*q2xq4*b+1)/
             (q3*q3+q4*q4+2*q3xq4+1)
              ).diff(b)+
         (1/(a*a*q1*q1+q3*q3+2*q1xq3*a+1)).diff(a)*
             (1/(a**2*q1**2*b*b+q2**2+q3**2*b**2+q4**2+2*q1xq2*a*b+
             2*q1xq3*a*b*b+2*q1xq4*a*b+2*q2xq3*b+2*q2xq4+2*q3xq4*b+1)/
             (a*a*b*b*q1*q1+q2*q2+2*q1xq2*a*b+1)/(b*b*q3*q3+q4*q4+2*q3xq4*b+1)/
             (q2*q2+q4*q4+2*q2xq4+1)
              ).diff(b)

      ).diff(a).diff(a) 

k2term = rggrf.roperation.Factorized((1-a)*(1-a)/(q1**2+1)**5/(q2**2+1)/(q3**2+1)/(q4**2+1),tmp) 
###k2term = rggrf.roperation.Factorized((1-a)*(1-a)/(q1**2+1)**6/(q2**2+1)**2/(q3**2+1)**2/(q4**2+1)**2,tmp)

#tmp =(1/(a*a*q1*q1+q2*q2+2*q1xq2*a+1)/(a*a*q1*q1+q3*q3+2*q1xq3*a+1)/
#        (q2*q2+q4*q4+2*q2xq4+1)/(q3*q3+q4*q4+2*q3xq4+1)/
#        (a**2*q1**2+q2**2+q3**2+q4**2+2*q1xq2*a-
#         2*q1xq3*a+2*q1xq4*a+2*q2xq3+2*q2xq4+2*q3xq4+1)+
#      1/(a*a*q1*q1+q2*q2+2*q1xq2*a+1)/(q3*q3+1)/
#        (q4*q4+1)/(q3*q3+q4*q4+2*q3xq4+1)/
#        (q3**2+q4**2+2*q3xq4+1)-
#      1/(q2*q2+1)/(a*a*q1*q1+q3*q3+2*q1xq3*a+1)/
#        (q2*q2+q4*q4+2*q2xq4+1)/(q4*q4+1)/
#        (q2**2+q4**2+2*q2xq4+1)
#      ).diff(a).diff(a).diff(a) 


#k2term = rggrf.roperation.Factorized((1-a)*(1-a)/(q1**2+1)**5/(q2**2+1)/(q3**2+1)/(q4**2+1),tmp)

s_prep =   ExpandScalarProdsAndPrepareFactorized(k2term)

#print "---------dm_%s_p%s --------- " %(idxL,idxK2)
sys.stdout.flush()
prepared_eqs.append(rggrf.integration.PrepareFactorizedNoSimplifyStrVars(s_prep, SPACE_DIM, ignore_unknown=True))
   
prog_names = rggrf.integration.GenerateMCCodeForGraphStrVars(base_name, prepared_eqs,SPACE_DIM, n_epsilon_series, NPOINTS, NTHREADS) 


res = rggrf.integration.CalculateEpsilonSeries(prog_names, build=True)
print res

print "With Sd: %s" %ResultWithSd(res, NLOOPS, n_epsilon_series)

print "Old Notation: %s" % ResultOldNotation(res)
#for idx in prog_names:
#    res = rggrf.integration.ExecMCCode(idx)
    