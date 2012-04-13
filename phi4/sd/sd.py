#!/usr/bin/python

import sympy
import copy
import sys

def xCombinations(seq, n):
    """Generator of all the n-element combinations of the given sequence.
    """
    if n == 0:
        yield seq[0:0]
    else:
        for i in range(len(seq)):
            for tail in xCombinations(seq[:i] + seq[i+1:], n - 1):
                yield seq[i:i+1] + tail

def xUniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xUniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc

def valid_vars(sector,used_vars, vars, cons):
   res=[]
   for i in range(len(vars)):
#      print i, used_vars
      if i in used_vars:
          continue
      t_set=set(used_vars[:-1]+[i])

      valid=reduce(lambda x,y: x and y, map(lambda x: (not x.issubset(t_set))and(x <>t_set), cons )+[True,True]) # to make reduce work with any length of cons
#      print i, t_set, valid, map(lambda x: (not x.issubset(t_set))and(x <>t_set), cons )
#      print cons[0],t_set, cons[0] not in t_set
      if valid:
          res.append(i)
   return res


class exp_pow:
    def __init__(self,tup2):
       self.a=tup2[0]
       self.b=tup2[1]

    def __add__(self,other):
       return exp_pow((self.a+other.a, self.b+other.b))

    def __repr__(self):
       return str((self.a,self.b))

class poly_exp:
    def __init__(self, poly, power, degree=None):
       self.poly = poly #list of monoms (monom -> list)
       if isinstance(power,tuple):
           self.power = exp_pow(power) #tuple (a,b) :  a+b*eps
       else:
           self.power = power #tuple (a,b) :  a+b*eps
 
       self.degree = degree

    def __repr__(self):
       return str((self.poly,self.power))
    
    def strech(self,svar,varlist):
       res=[]
       for monom in self.poly:
          factor=[]
          for var in monom:
             if var in varlist:
                factor.append(svar)
          res.append(copy.copy(monom)+factor)
       return poly_exp(res,self.power,degree=self.degree)

    def extract(self,varlist):
       res=copy.deepcopy(self.poly)
       for monom in res:
#          print monom, varlist
          for var in varlist:
             monom.remove(var)
       return poly_exp(res,self.power,self.degree)
        
           

def decompose(sector, poly_lst, vars, cons):
    res = [copy.deepcopy(x) for x in poly_lst]
    used_vars = []
    extracted=dict()
    for var in sector:
        sector_idx=sector.index(var)
        used_vars.append(var)
        v_vars = valid_vars(sector, used_vars, vars, cons)

#        print
#        print var,v_vars
        res_n=[]
        for poly in res:
            idx=res.index(poly)
            poly=poly.strech(var,v_vars)
         
            if poly.degree<>None:
                if idx  not in extracted:
                     extracted[idx]=poly_exp([[]],poly.power)
                extracted[idx].poly[0]+=[var,]*(poly.degree-sector_idx)
#                print
#                print poly
                poly=poly.extract([var,]*(poly.degree-sector_idx))
#                print poly
#                print
            res_n.append(poly)
        res=res_n

#        print "\n ---\n %s \n ---\n"%res

     
    for poly in extracted.values():
       res.append(poly)
                
    return res

def poly_list2sympy(poly_list):
   res=sympy.Number(1)
   eps=sympy.var('eps')
   for epoly in poly_list:
       res*=(epoly.poly)**(epoly.power[0]+epoly.power[1]*eps)
   return res


def monom2str(monom):
#   print monom
   if len(monom)==0:
       return "1"
   res=""
   for var in monom:
      res=res+"u%s*"%var
   return res[:-1]

def poly2str(poly):
   if len(poly)==0:
      return "1"
   else:
      res=""
      for monom in poly:
          res+="%s+"%monom2str(monom)
      return res[:-1]


def poly_list2ccode(poly_list):
   res=""
   factor=dict()

#   print "---"
#   print poly_list
   for poly in poly_list:
       if len(poly.poly)==0:
          pass
       elif len(poly.poly)==1:
          for var in poly.poly[0]:
              if var not in factor:
                 factor[var]=exp_pow((0,0))
              factor[var]+=poly.power
       else:
          t_poly=poly2str(poly.poly)
          # eps = 0 !!!!
          res+= "pow(%s,%s)*"%(t_poly, poly.power.a)

   for var in factor.keys():
       # eps = 0 !!!!
       power=factor[var]
       if power.a == 0:
          continue
       else:
          if power.a ==1:
              res+="(u%s)*"%(var)
          else:
              res+="pow(u%s,%s)*"%(var,power.a)
   return res[:-1]

def functions(poly_dict,vars):
    res2="""
void func(double k[DIMENSION], double f[FUNCTIONS])
{
f[0]=0.;
"""
    cnt=0
    res=""
    varstring=""
    varstring2=""
    for i in range(len(vars)-1):
        varstring+="double w_%s,"%i
        varstring2+="k[%s],"%i
    varstring=varstring[:-1]
    varstring2=varstring2[:-1]
    for sector in poly_dict.keys():
        res+="""
double func%s( %s)
{
//sector %s
"""%(cnt,varstring,sector)
        cnt2=0
        for var in vars:
            if vars.index(var)<>sector[0]:
                res+="double %s=w_%s;\n"%(var,cnt2)
                cnt2+=1
        expr=poly_dict[sector]
        res+="double res = %s;\n return res;\n}\n"%expr
        res2+="f[0]+=func%s(%s);\n"%(cnt,varstring2)
        cnt+=1
    return res + res2 + "}\n"

def code(func,N):
    res="""
#include <math.h>
#include <stdio.h>
#include <vegas.h>
#include <stdlib.h>
#define gamma tgamma
#define DIMENSION %s
#define FUNCTIONS 1
#define ITERATIONS 5
#define NTHREADS 2
#define NEPS 0
#define NITER 2
double reg_initial[2*DIMENSION]={%s};

"""%(N-1, ("0.,"*(N-1)+"1.,"*(N-1))[:-1])
    res+=func + """
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
    return res
    
## e123-e23-e3-e-
"""
N=6
L=3
cons=map(set,[[0,1,2],[0,3,5],[1,3,4],[2,4,5]])
name="sd7_3loop_1_"
"""
##

## e123-e24-35-45-e5-e-
N=10
L=5
cons = [frozenset([8, 9, 6]),
    frozenset([0, 1, 2, 4, 7, 9]), 
    frozenset([1, 3, 4, 5, 6, 7, 9]), 
    frozenset([0, 3, 4, 6, 8, 9]), 
    frozenset([1, 2, 3, 4, 6, 8, 9]), 
    frozenset([0, 2, 3, 5, 6]), 
    frozenset([9, 2, 5, 6, 7]), 
    frozenset([0, 1, 5, 6, 7, 9]), 
    frozenset([0, 2, 3, 5, 8, 9]), 
    frozenset([8, 9, 2, 4, 5]), 
    frozenset([0, 1, 2, 6, 8, 9]), 
    frozenset([0, 1, 2]), 
    frozenset([1, 2, 3, 9, 7]), 
    frozenset([2, 4, 5, 6]), 
    frozenset([0, 1, 4, 5, 8, 9]), 
    frozenset([8, 1, 3, 5, 9]), 
    frozenset([1, 2, 3, 4]), 
    frozenset([0, 2, 3, 4, 5, 7, 8]), 
    frozenset([1, 3, 5, 6]), 
    frozenset([9, 4, 7]), 
    frozenset([8, 0, 3, 6, 7]), 
    frozenset([0, 1, 5, 8, 7]), 
    frozenset([1, 3, 4, 5, 7, 8]), 
    frozenset([0, 1, 4, 5, 6]), 
    frozenset([0, 9, 3, 7]), 
    frozenset([1, 2, 3, 6, 7, 8]), 
    frozenset([8, 2, 5, 7]), 
    frozenset([0, 3, 4]), 
    frozenset([0, 2, 3, 4, 5, 6, 7, 9]), 
    frozenset([0, 1, 2, 4, 6, 7, 8]), 
    frozenset([8, 4, 6, 7])]
name="sd7_5loop_1_"

sect=[]
for i in xCombinations(range(N),L):
    good=True
    for constr in cons:
       if constr.issubset(i):
           good=False
           break

    if good:
        sect.append(i)

print "//nsectors ",len(sect)

sect1=[]
cnt=20
for i in range(20):
   sector=sect[i] 
   sect1.append(sector)

det=[]
for i in xUniqueCombinations(range(N),L):
    good=True
    for constr in cons:
       if constr.issubset(i):
           good=False
           break

    if good:
        det.append(i)

print "// ",len(det)
print "// det=",det

#print sect
#print len(sect)
#print det


#polynom=poly_exp([[1,2,3],[1,2,4]],(1,0))
#print polynom
#print polynom.strech(1,[2,3,4])

u=sympy.var(reduce(lambda x,y:x+y,['u%s '%i for i in range(N)]))
#print u
det_s=0.
for term in det:
   term_s=1
   for ui in term:
       term_s=term_s*u[ui]
   det_s=det_s+term_s

print "//det generated"

det_p=poly_exp(det,(-2,0),L)
u_p=poly_exp([range(N)],(1,0))
u_mp=poly_exp([range(N)],(-1,0))

sect_expr=dict()

Nf=1000


for sector in sect:
#for sector in sect1:
    idx=sect.index(sector)
    if (idx+1) % Nf == 0:
        print "write to disk... %s"%(idx+1)
        f=open("%s%s.c"%(name,idx/Nf),'w')
        f.write(code(functions(sect_expr, u), N))
        f.close()
        sect_expr=dict()

#    print "//generating %s/%s %s"%(sect.index(sector),len(sect),sector)
    sys.stdout.flush()
    poly_list = decompose(sector,[det_p,u_p],u,cons) + [u_mp]
#    print poly_list
#    expr = poly_list2sympy(poly_list)*u[sector[0]]
    sect_expr[tuple(sector)] = poly_list2ccode(poly_list+[poly_exp([[sector[0]]],(1,0))])

if len(sect_expr)<>0:
    print "write to disk... %s"%(idx+1)
    f=open("%s%s.c"%(name,idx/Nf),'w')
    f.write(code(functions(sect_expr, u), N))
    f.close()
    sect_expr=dict()
    
    


#poly_list = decompose([0,1,3],[det_p,u_p],u,cons) + [u_mp]
#print poly_list2sympy(poly_list)





