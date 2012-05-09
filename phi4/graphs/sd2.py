#!/usr/bin/python
# -*- coding:utf8
from comb import xCombinations, xUniqueCombinations
#import sympy
import copy
import sys
import sympy
from methods.feynman_tools import find_eq,  qi_lambda,  apply_eq,  conv_sub,  merge_grp_qi
import conserv
import subgraphs
from methods.feynman_tools import strech_indexes, dTau_line


def FindExtendedTadpoles(graph):
    def key_by_value(_dict, value):
        res=list()
        for key in _dict:
            if value==_dict[key]:
                res.append(key)
        if len(res)==0:
            raise ValueError,  "no such value in dict %s"%(str(value))
        elif len(res)>1:
            raise ValueError,  "multiple values in dict:%s"%res
        else:
            return res[0]
    
    def check_subsets(_subgraphs):
        for sub in _subgraphs:
#            print "sub=", sub
            for sub2 in _subgraphs:
                if sub==sub2:
                    continue
                if sub2.isSubSet(sub) or sub.isSubSet(sub2):
#                    print sub,  sub2
                    return False
        return True
    
    graph_as_sub=graph.asSubgraph()
    if graph_as_sub.CountExtLegs()==2:
        lst=[graph_as_sub]
    else:
        lst=[]
    sub_comb=dict()
    for i in range(2, len(graph._subgraphs)):
        for subs in xUniqueCombinations(range(len(graph._subgraphs)), i):
#            print "subs = ", subs
            c_subsets=check_subsets([graph._subgraphs[x] for x in subs])
            if not c_subsets:
#                print "check_subsets : " , subs,   c_subsets
                continue
            sub_u=graph._subgraphs[subs[0]]
            for sub in subs[1:]:
                _sub=graph._subgraphs[sub]
                sub_u=sub_u+_sub
                
            if sub_u. isSubgraph1PI() : #we need connected subgraph, but in our case sum of 1pi subgraphs must be 1pi if connected.
#                print "sub_u", sub_u
                sub_comb[tuple(subs)]=sub_u
#    sub_comb=dict()
#    sub_comb[tuple([0, 1])]=graph._subgraphs[0]+graph._subgraphs[1]
    _tadpoles=list()
    for sub in lst+graph._subgraphs:
#        print "start:",  sub,  sub_comb.keys()
        tadpoles=sub._CheckTadpoles(sub_comb.values(), check_equal=True)
#        print tadpoles
        if len(tadpoles)>0:
#            print "subgraph:",  sub
            for tadpole in tadpoles:
#                print "tadpoles", tadpoles
#                print "   tadpole: ", tadpole,  key_by_value(sub_comb, tadpole)
                _tadpoles.append(tuple(map(lambda x:x+1000,  key_by_value(sub_comb, tadpole))))
    graph._tadpoles=_tadpoles
    print "tadpoles=", _tadpoles

            

def Prepare(graph, model):
    model.SetTypes(graph)
    model.checktadpoles=False
    graph.FindSubgraphs(model)
    
    subs_toremove=subgraphs.DetectSauseges(graph._subgraphs)
    graph.RemoveSubgaphs(subs_toremove)

    subgraphs.RemoveTadpoles(graph)
    
    for i in range(len(graph._subgraphs)):
        print "sub %s : %s"%(i, graph._subgraphs[i])
        
    FindExtendedTadpoles(graph)
#    raise Exception,  "force quit"
    
    int_edges=graph._internal_edges_dict()
    cons = conserv.Conservations(int_edges)
    eqs = find_eq(cons)
    print
#    print cons, eqs
    cons=apply_eq(cons, eqs)
    print "Conservations:\n", cons
    graph._cons=cons
    graph._qi, graph._qi2l = qi_lambda(cons, eqs)
    print graph._qi, graph._qi2l
    print "lines = ", graph.Lines()
    graph._eq_grp_orig=graph._eq_grp
    graph._eq_grp=merge_grp_qi(graph._eq_grp, graph._qi2l)

    graph._det=gendet(cons, graph._subgraphs, graph._qi, graph.NLoops())
#    print graph._det
#    print len(gensectors(cons, graph._qi,  graph.NLoops()))
    graph._sectors=gensectors(cons, graph._qi, graph.NLoops())
    
"""
    det_ = det(cons, graph._subgraphs,  graph.NLoops())
    Cdet=sympy.Number(0)
    if len(graph.ExternalLines())==2:
        int_edges[1000000]=[i.idx() for i in graph.ExternalNodes()]
        cons = conserv.Conservations(int_edges)
        eqs = find_eq(cons)
        cons=apply_eq(cons, eqs)        
        Cdet = - det(cons, graph._subgraphs,  graph.NLoops()+1)
    
    graph._det_f=det_
    graph._cdet=Cdet
"""

def valid_vars(sector,used_vars, vars, cons):
   res=[]
   for i in vars:
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
        if isinstance(other, int):
            return exp_pow((self.a+other, self.b))
        else:
            return exp_pow((self.a+other.a, self.b+other.b))

    def __sub__(self,other):
        if isinstance(other, int):
            return exp_pow((self.a-other, self.b))
        else:
            return exp_pow((self.a-other.a, self.b-other.b))


    def __repr__(self):
       return str((self.a,self.b))

class poly_exp:
    def __init__(self, poly, power, degree=None, coef=(1, 0)):
       self.poly = poly #list of monoms (monom -> list)
       if isinstance(power,tuple):
           self.power = exp_pow(power) #tuple (a,b) :  a+b*eps
       else:
           self.power = power #tuple (a,b) :  a+b*eps
 
       self.degree = degree
       if isinstance(coef,tuple):
           self.coef = exp_pow(coef) #tuple (a,b) :  a+b*eps
       else:
           self.coef = coef #tuple (a,b) :  a+b*eps
       

    def __repr__(self):
       return "(c=%s,%s,pow=%s)"%(self.coef, self.poly,self.power)
    
    def strech(self,svar,varlist):
       res=[]
       for monom in self.poly:
          factor=[]
          for var in monom:
             if var in varlist:
                factor.append(svar)
          res.append(monom+factor)
       return poly_exp(res,self.power,self.degree,  self.coef)

    def extract(self,varlist):
#       print
       res=[]
       for i in range(len(self.poly)):
           
          monom=copy.copy(self.poly[i])
#          print 
#          print i, res
#          print monom, varlist
          for var in varlist:
             monom.remove(var)
          res.append(monom)
       return poly_exp(res,self.power,self.degree, self.coef)

    def set0_list(self, var_list):
        res=[]
        for monom in self.poly:
            if len(set(var_list)&set(monom))==0:
                res.append(monom)
        return res

    def set0(self, var):
        res=[]
        for monom in self.poly:
            if var not in monom:
#                res.append(copy.copy(monom))
                res.append(monom)
        return poly_exp(res,self.power,self.degree, self.coef)
            
    def set1(self, var):
        res=[]
        for monom in self.poly:
            monom_=copy.copy(monom)
            if var in monom:
                for i in range(monom.count(var)):
                    monom_.remove(var)
            res.append(copy.copy(monom_))
        return poly_exp(res,self.power,self.degree, self.coef)
        
    def diff(self, var):
        res=copy.copy(self.poly)
        diff_=[]
        for monom in self.poly:
            monom_=copy.copy(monom)
            if var in monom:
                for i in range(monom.count(var)):
                    monom_.remove(var)
                for i in range(monom.count(var)):
                    diff_.append(monom_)
        if len(diff_)==0:
            return []
        else:
            return [poly_exp(diff_,(1, 0), coef=self.power), poly_exp(res,self.power-1,self.degree, self.coef)]
    
    def GCD(self):
#        print self
        gcd=self.poly[0]
        for monom in self.poly[1:]:
            gcd_=[]
            for var in set(gcd):
                gcd_+=[var, ]*(min(gcd.count(var), monom.count(var)))
            gcd=gcd_
        return poly_exp([gcd], self.power, self.degree)
    
    
def diff_poly_lst(poly_lst, var):
    terms=[]
    for poly in poly_lst:
        poly_lst_=[]
        for poly2 in poly_lst:
            if poly<>poly2:
                poly_lst_.append(copy.copy(poly2))
        
        pd=poly.diff(var)
        if len(pd)<>0:
            terms.append(poly_lst_+pd)
    return terms
           
def set0_poly_lst(poly_lst, var):
    res=[]
#    print "===="
#    print poly_lst
    for poly in poly_lst:
#        print "========="
#        print poly
        poly_=poly.set0(var)
        if len(poly_.poly)>0:
#            print "========="
#            print poly

            gcd=poly_.GCD()
#            print poly_
#            print gcd

            if len(gcd.poly[0])>0:
                res.append(poly_.extract(gcd.poly[0]))
                res.append(gcd)
            else:
                res.append(poly_)
#        elif len(poly_.poly)==1:
#            res.append(poly_)
        else: 
            if poly_.power.a>0:
                return []
            else:
                raise ZeroDivisionError,  "var:=%s poly=%s"%(var, poly)
    return res
    
def set1_poly_lst(poly_lst, var):
    res=[]
    for poly in poly_lst:
        res.append(poly.set1(var))
    return res


def decompose(sector, poly_lst,  jakob=True):
#    print sector, poly_lst
    res = copy.copy(poly_lst)
    extracted=dict()
    jakob_poly=[]
    sector_idx=-1
    for var in sector.sect:
        sector_idx+=1
        v_vars = sector.var[sector_idx]
        jakob_poly+=[var]*len(v_vars)
#        print
#        print var,v_vars
        res_n=[]
        idx=-1
        for poly in res:
            idx+=1
            poly=poly.strech(var,v_vars)
         
            if poly.degree<>None:
                if idx  not in extracted:
                     extracted[idx]=poly_exp([[]],poly.power)
                extracted[idx].poly[0]+=[var,]*(poly.degree-sector_idx)
#                print
#                print poly
#                print [var,]*(poly.degree-sector_idx)
                poly=poly.extract([var,]*(poly.degree-sector_idx))
#                print poly
#                print
            res_n.append(poly)
        res=res_n
#        print "-----"
#        print var,  v_vars, res

#        print "\n ---\n %s \n ---\n"%res

     
    for poly in extracted.values():
       res.append(poly)
       
    if jakob:
        res.append(poly_exp([jakob_poly], (1, 0), coef=(1, 0)))
                
    return factorize_poly_lst( res)

def monom2str(monom):
#   print monom
    if len(monom)==0:
        return "1"
    res=""
    sign=1
    for var in monom:
        if var<0:
            sign=-sign
        res=res+"u%s*"%abs(var)
    if sign>0:
        return res[:-1]
    else:
        return "(-%s)"%res[:-1]

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
    #eps=0
    C=1.
    if len(poly_list)==0:
        return "0."
#    print "---"
#    print poly_list
    for poly in poly_list:
#        print poly,  len(poly.poly)
        if len(poly.poly)==0:
            pass
        elif len(poly.poly)==1:
            for var in poly.poly[0]:
                if var not in factor:
                    factor[var]=exp_pow((0,0))
                factor[var]+=poly.power
        else:
            t_poly=poly2str(poly.poly)
#            print t_poly
            # eps = 0 !!!!
            if poly.power.a==1:
                res+= "(%s)*"%(t_poly)
            elif poly.power.a==0:
                res+= "(1.)*"
            else:
                res+= "pow(%s,%s)*"%(t_poly, poly.power.a)
        C=C*poly.coef.a
#    print res,  poly.power.a
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
#    print C
#    print res
    if C==1:
        return res[:-1]
    else:
        return "%s(%s)"%(res, C)

def functions(poly_dict, vars,  strechs,  index=None):
    if index==None:
        sindex=""
    else:
        sindex="_t_%s"%index
    res2="""
double func%s(double k[DIMENSION])
{
double f=0.;
"""%sindex
    cnt=0
    res=""
    varstring=""
    varstring2=""
    for i in range(len(vars)+len(strechs)-1):
        varstring+="double w_%s,"%i
        varstring2+="k[%s],"%i
    varstring=varstring[:-1]
    varstring2=varstring2[:-1]
    for sector in poly_dict.keys():
        res+="""
double func%s_%s( %s)
{
//sector %s
"""%(cnt,index, varstring,sector)
        cnt2=0
        
        s0="1./(1.+"
        for var in vars+strechs:
            if var<>sector.sect[0]:
                res+="double u%s=w_%s;\n"%(var,cnt2)
                cnt2+=1
        
        

        expr, subs=poly_dict[sector]
        res+="double u%s=1./(1.+%s);\n"%(sector.sect[0],subs)
        res+="double res = %s;\n return res;\n}\n"%expr
        res2+="f+=func%s_%s(%s);\n"%(cnt,index, varstring2)
        cnt+=1
    return res + res2 + "return f;}\n"

def code( Nf, N,  func_fname):
    include=""
    func="""
void func(double k[DIMENSION], double f[FUNCTIONS])
{
f[0]=0.;
"""
    for i in range(Nf+1):
        func+="""
f[0]+=func_t_%s(k);
"""%i
        include+="#include \"%s_%s.h\"\n"%(func_fname, i)
    func+="}\n\n"
        
    
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

%s

double reg_initial[2*DIMENSION]={%s};

"""%(N-1, include,  ("0.,"*(N-1)+"1.,"*(N-1))[:-1])
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


def code_f(func,N):
    res="""
#include <math.h>
#define DIMENSION %s
"""%(N-1)
    res+=func 
    return res
    
def code_h(idx, N):
    res="""
#include <math.h>
#define DIMENSION %s
double func_t_%s(double k[DIMENSION]);

"""%(N-1, idx)

    return res




def check_comb(term, cons):
    res=True
    for constr in cons:
        if constr.issubset(term):
            res=False
            break
    return res
    
    
def strech_list(sector, subgraphs_):
    """ generate list of strechs extracted in leading term by first pass of sector decomposition
    """
    strechs=[]
    subs=conv_sub(subgraphs_)
    for j in range(len(subs)):
        si=len(set(sector)&set(subs[j]))-subgraphs_[j].NLoopSub()
        strechs+=[1000+j]*si
    return list(set(strechs))


def gensectors(cons,vars, L):
    sect=[]
    for i in xCombinations(vars.keys(), L):
        if check_comb(i, cons):
            sect.append(i)            
    return sect

def gendet(cons, subgraphs_, vars, L):
    det=[]
    subs=conv_sub(subgraphs_)
    for i in xUniqueCombinations(vars.keys(),L):
        if check_comb(i, cons):
            det.append(i+strech_list(i, subgraphs_))
    return det
    
def minus(poly_list):
    if len(poly_list)==0:
        return []
    res=copy.deepcopy(poly_list)
    res[0].coef=exp_pow((0, 0))-res[0].coef
    return res

def factorize_poly_lst(poly_lst):
    res=[]
    for poly in poly_lst:
        if poly.coef.a==0 and poly.coef.b==0:
            return []
        if (len(poly.poly)==1):
           if (len(poly.poly[0])==0) and float(poly.coef.a)==1.:
                #print poly
                continue
           else:
                res.append(poly)
                continue
        gcd=poly.GCD()
        if len(gcd.poly)==1: 
            if len(gcd.poly[0])<>0:
#                print "factorize", gcd.poly,  poly,  poly.extract(gcd.poly[0])
                res.append(gcd)
                res.append(poly.extract(gcd.poly[0]))
            elif len(gcd.poly[0])==0:
#                print "factorize2", poly
                res.append(poly)
        else:
            raise Exception,  "GCD must be monomial, poly=%s, gcd=%s"%(poly, gcd)
#    print "FACTORIZE",  res
    return res

def split_u_a(monom):
    res_a=[]
    res_u=[]
    for var in monom:
        if abs(var)<1000:
            res_u.append(var)
        else:
            res_a.append(var)
    return (res_u, res_a)
    
def find_bad_poly(term):
    res=list()
    for poly in term:
        if poly.power.a<0 and len(poly.poly)>1:
            splitted=map(split_u_a, poly.poly)
            u_, a_=zip(*splitted)
            if min(map(len, u_))<>0:
                res.append((poly, []))
            else:
                a__=a_[u_.index([])]
                if len(a__)>0:
                    res.append((poly, a__)) 
    return res

def split_sector_dict(sector_terms):
    good_terms=dict()
    bad_terms=dict()
    for sector in sector_terms:
        good_terms[sector]=[]
        bad_terms[sector]=[]
        for term in sector_terms[sector]:
#            print
#            print sector
#            print term
            term_=factorize_poly_lst(term[0])
            bp_list=find_bad_poly(term_)
            if len(bp_list)>0:
                for bp in bp_list:
                    bad_terms[sector].append((term_, term[1]))
            else:
                good_terms[sector].append((term_, term[1]))
        if len(good_terms[sector])==0:
            del good_terms[sector]
        if len(bad_terms[sector])==0:
            del bad_terms[sector]            
    return (good_terms,  bad_terms)
            
            
def combine_dicts(dict1, dict2):
    res=dict()
    for key in dict1:
        res[key]=copy.copy(dict1[key])
    for key in dict2:
        if key in res:
            res[key]=res[key]+dict2[key]
        else:
            res[key]=copy.copy(dict2[key])
    return res

class sect:
    def __init__(self,  sect_list,  var_list):
        if len(sect_list)<>len(var_list):
            raise ValueError,  " sect_list and var_list must be the same length (%s,%s)"%(len(sect_list), len(var_list))
        self.sect=sect_list
        for vars in var_list:
            vars.sort()
        self.var=var_list
    
    def  add_sector(self,  sector_var,  strech_vars):
        self.sect.append(sector_var)
        self.var.append(sorted(strech_vars))
    
    def __str__(self):
        return "(%s,%s)"%(self.sect, self.var)
        
    def __repr__(self):
        return str(self)
    
    def __hash__(self):
        return str(self).__hash__()
        
    def __add__(self, other):
        return sect(self.sect+other.sect,  self.var+other.var)
        
def max_monom_degree(poly):
    return max([len(set(term))  for term in poly])
        
def poly_vars(poly):
    res=set()
    for term in poly:
        res=res|set(term)
    return list(res)
    
        
        
def find_zeroes(polyexp, level=10000000):
    poly=polyexp.poly
    level_=min(level, len(poly_vars(poly)))
#    print "level %s"%level_ 
    zeroes=list()
    for i in xrange(level_):
        for uu in xUniqueCombinations(poly_vars(poly), i):
            polyexp_=copy.copy(polyexp)
            
            if len(polyexp_.set0_list(uu))==0:
                zeroes.append(uu)
    return zeroes
    
def minimal_zeroes(zeroes,  nostrechs=False):
    res=[]
    for zero in sorted(zeroes, key=len):
        good=True
        for z1 in res:
            if set(z1).issubset(set(zero)):
                good=False
                break
        if good and nostrechs:
            for z in zero:
                if abs(z)>=1000:
                    good=False
                    break
        if good:
            res.append(zero)
    return res

def diff_subtraction(term,  strechs):
    """ perform diff subtraction for ALL strechs that wasn't affected by direct_subtraction
    N.B. output differs from that if direct_subtraction (no need to store affected strechs)
    """
    res=[term[0]]
    for var in strechs:
        if var in term[1] and term[1][var]>=0:
            continue
        terms_=[]
        if strechs[var]==0:
            for term_ in res:
                terms_.append(set1_poly_lst(term_, var))
        elif strechs[var]==1:
            for term_ in res:
                terms_+=diff_poly_lst(term_, var)
        elif strechs[var]==2:
            for term_ in res:
                firstD=diff_poly_lst(term_, var)
                for term_ in firstD:
                    seconD=diff_poly_lst(term_, var)
                    for term__ in seconD:
##не работает если переменная имеет индекс 0                                    
                        term__.append(poly_exp([[], [-var]], (1, 0)))
                        terms_+=[term__]
        else:
            raise NotImplementedError,  "strech level   = %s"%strechs[var]
        res=terms_    
    return res

"""
            for var in strechs:
#                print var,  strechs[var] ,   var in active_strechs[sector]
                if var in active_strechs[sector] or strechs[var]==0:
                    continue
#                print "---"
                terms_=[]
                if strechs[var]==1:
                    for term in terms:
                        terms_+=diff_poly_lst(term, var)
                elif strechs[var]==2:
                    for term in terms:
                        firstD=diff_poly_lst(term, var)
                        for term_ in firstD:
                            seconD=diff_poly_lst(term_, var)
                            for term__ in seconD:
##не работает если переменная имеет индекс 0                                    
                                term__.append(poly_exp([[], [-var]], (1, 0)))
                                terms_+=[term__]
                else:
                    raise NotImplementedError,  "strech level   = %s"%strechs[var]
#                print terms_
                terms=terms_    
"""    

def get_tadpole_constrains(var,  strech_dict,  tadpoles):
    to_unit=list()
    zeroes=list()
    unity=list()
#    print var, strech_dict
    for strech in strech_dict:
        if strech_dict[strech]==0:
            zeroes.append(strech)
        elif strech_dict[strech]==1:
            unity.append(strech)
    s_zeroes=set(zeroes+[var])
    for tadpole in tadpoles:
        rest=list(set(tadpole)-s_zeroes)
        if len(rest)==1:
            if rest[0] not in unity:
                to_unit.append(rest[0])
        elif len(rest)==0:
            raise ValueError,  "combination of vars set to zero (%s) is equal to constrain %s"%(tadpole, s_zeroes)
    return to_unit
            
def set_termvar_to0_minus(term, var, units):
    expr=minus(set0_poly_lst(term[0], var))
    vars=term[1].copy()
    vars.update({var:0})
    for var in units:
#        expr=set1_poly_lst(expr, var)
        vars.update({var:-1})
    return (expr, vars)

def direct_subtraction(term, strechs,  tadpoles,  drop_azero_terms=False):
    """ strechs -> dict of strechs to be subtracted
    """
    res=[term]
#    print "direct_subtraction:",  term
#    print "strechs", strechs
    zterms=list()
    comulative_term1=term[1]
    for var in sorted(strechs.keys()): 
        if var in term[1] and term[1][var]>=0:
            raise ValueError,  "can't perform subtraction on var=%s, term[1]=%s, strechs=%s"%(var, term[1], strechs)
        terms_=list()
        zterms_=list()
        if strechs[var]==0:
            for term_ in res:
#                if var in term_[1]:
#                    continue
                vars=term_[1].copy()
                vars.update({var:1})
                terms_.append((set1_poly_lst(term_[0], var),  vars))
        elif strechs[var]==1:
            for term_ in res:
#                if var in term_[1]:
#                    continue

                if not (drop_azero_terms or (var in term_[1] and term_[1][var]==-1)):
#                    print term_
#                    terms_.append((minus(set0_poly_lst(term_[0], var)), combine_dicts(term_[1], {var:0}) ))
#                    print var,  term_[1],  tadpoles
                    to_unit=get_tadpole_constrains(var, term_[1],  tadpoles)
#                    print var,  to_unit
#                    print poly_list2ccode(term_[0])
                    
                    
                    zterms_.append(set_termvar_to0_minus(term_, var, to_unit))
                vars=term_[1].copy()
                vars.update({var:1})
                terms_.append((set1_poly_lst(term_[0], var),  vars))

        elif strechs[var]==2:
            for term_ in res:
                firstD=diff_poly_lst(term_[0] , var)
                vars=term_[1].copy()
                vars.update({var:1})
                terms_.append((set1_poly_lst(term_[0], var), vars ))
                if not (drop_azero_terms or (var in term_[1] and term_[1][var]==-1)):
#                    terms_.append((minus(set0_poly_lst(term_[0], var)),  combine_dicts(term_[1], {var:0}) ))
                    to_unit=get_tadpole_constrains(var, term_[1],  tadpoles)
#                    print var,  to_unit

                    zterms_.append(set_termvar_to0_minus(term_, var, to_unit) )
                    for term__ in firstD:
#                        terms_.append((minus(set0_poly_lst(term__, var)), combine_dicts(term_[1], {var:0}) ))
                        terms_.append(set_termvar_to0_minus((term__, term_[1]), var, to_unit) )                       
        else:
            raise NotImplementedError,  "strech level   = %s"%strechs[var]

        res=terms_
        zterms+=zterms_
#    res=[(term_, term[1]+strechs.keys()) for term_ in res]
    return res+zterms

###    for var in vars:
###        if var not in active_strechs[sector_] and strechs[var]<>0:
###            continue
###            
###        terms_=[]
###        if strechs[var]==0:
###            for term in terms:
###                terms_.append(set1_poly_lst(term, var))
###        elif strechs[var]==1:
###            for term in terms:
###                if not drop_azero_terms:
###                    terms_.append(minus(set0_poly_lst(term, var)))
###                terms_.append(set1_poly_lst(term, var))
###        elif strechs[var]==2:
###            for term in terms:
###                firstD=diff_poly_lst(term, var)
###                terms_.append(set1_poly_lst(term, var))
###                if not drop_azero_terms:
###                    terms_.append(minus(set0_poly_lst(term, var)))
###                     for term_ in firstD:
###                        terms_.append(minus(set0_poly_lst(term_, var)))
###        else:
###            raise NotImplementedError,  "strech level   = %s"%strechs[var]
###
###        terms=terms_


def save_sectors(g1, sector_terms, strech_vars, name_, idx):

        sect_terms=dict()
        for sector in sector_terms.keys():
            
#            print "sector= ",  sector
#            print "qi = ", g1._qi
            subs=[[x] for x in g1._qi.keys()]
            subs.remove([sector.sect[0]])
            
            subs_polyl=decompose(sect(sector.sect[1:], sector.var[1:]), [poly_exp(subs,  (1, 0))] , jakob=False)
            

            terms=sector_terms[sector]
            tres=""
            for term in   terms:
                f_term=factorize_poly_lst(term)
                tres+="%s;\nres+="%poly_list2ccode(f_term)
            sect_terms[sector]=(tres[:-5], poly_list2ccode(subs_polyl))


#        print
#        print "write to disk... %s"%(idx+1)
        f=open("tmp/%s_func_%s.c"%(name_,idx),'w')
        f.write(code_f(functions(sect_terms, g1._qi.keys(), strech_vars, idx), len(g1._qi.keys())+len(strech_vars)))
        f.close()
        f=open("tmp/%s_func_%s.h"%(name_,idx),'w')
        f.write(code_h( idx, len(g1._qi.keys())+len(strech_vars)))
        f.close()

def save_sd(name, g1,  model):
    #print g1._eq_grp
    if len(g1._subgraphs)==0:
        no_dm2=True
	g1._eq_grp=[None]
    else:
        no_dm2=False

    for grp_ in g1._eq_grp:
        if (not no_dm2) and len(grp_)==0:
            continue
        print grp_  ,  g1._qi, 
	if not no_dm2:
            print list(set(grp_)& set(g1._qi))
        else:
            print

        ui=reduce(lambda x, y:x+y,  [[qi_]*(g1._qi[qi_]-1) for qi_ in g1._qi])

#        print ui
#        qi=g1._qi.keys()[0]

	if not no_dm2:
            qi=list(set(grp_)&set(g1._qi))[0]
            ui.append(qi)
        else:
            qi="O"
        name_="%s_%s_"%(name, qi)

        print "   term u%s"%qi
        print ui,  g1._eq_grp
        sub_idx=-1
        for sub in g1._subgraphs:
            sub_idx+=1
            sub._strechvar=1000+sub_idx
            print "%s sub = %s"%(sub._strechvar,  sub)
    
        lfactor=1.
##        for qi_ in g1._qi.keys():
###            if qi_==qi:
###                lfactor=lfactor/sympy.factorial(g1._qi[qi_])
###            else:
##                lfactor=lfactor/sympy.factorial(g1._qi[qi_]-1)
    
        for qi_ in g1._qi.keys():
            if (not no_dm2) and qi_==qi:
                lfactor=lfactor/sympy.factorial(g1._qi[qi_])
            else:
                lfactor=lfactor/sympy.factorial(g1._qi[qi_]-1)


        if not no_dm2:
            grp=None
            for grp in g1._eq_grp:
                if qi in grp:
                    break
            grp_factor=len(grp)
        else:
            grp_factor=1.
    
        print lfactor, g1.sym_coef(), grp_factor 
    
        A1=poly_exp(g1._det, (-2, 0),  coef=(float(lfactor*g1.sym_coef()*grp_factor ), 0))
 ##       A1=poly_exp(g1._det, (-2, 0),  coef=(1., 0))

        zeroes=minimal_zeroes(find_zeroes(A1) ) 
        print "Zeroes %s:\n%s\n"%(len(zeroes), zeroes)
        print "DET=", A1
#        print "DET0=", set0_poly_lst([A1], 1000)
        A2=poly_exp([ui, ], (1, 0))
        A3=poly_exp([g1._qi.keys()], (1, 0))
        A4=poly_exp([g1._qi.keys()], (-1, 0))
        if not no_dm2:
            g_qi=dTau_line(g1, qi,  model)
        else:
            g_qi=g1

        strechs=strech_indexes(g_qi, model)
        print "strechs = ", strechs
        #print [A1, A2, A3 ]
        
        strech_vars=[]
        for var in strechs:
            if strechs[var]>0:
                strech_vars.append(var)
                
        Nf=1000
#        Nf=10

        
#        g1._sectors=[[9, 8, 5]]

#        g1._sectors=[[8, 11, 12, 7, 6]]
#        g1._sectors=[[12, 13, 7, 10, 11]]
#        g1._sectors=[[7, 8, 10, 11, 12]]
#        g1._sectors=[[12, 13, 10, 9, 8]]
#        g1._sectors=[[13, 11, 12, 10, 7]]
        drop_azero_terms=False
        second_decompose=True  # for debugging
#        second_decompose=False
#        (second_decompose, drop_azero_terms)=(False,  True)
        
        sector_terms=dict()
        
        idx=-1
        idx_save=0
        Nsaved=0
        for sector in g1._sectors:
	    current_terms=dict()
            idx+=1
            vars_lst=[]
            used_vars=[]
            for var in sector:
                used_vars.append(var)
                vars_lst.append( valid_vars(sector, used_vars, g1._qi, g1._cons))
            sector_=sect(sector, vars_lst)
#            print sector_
            
            
            
            if (idx+1) % (Nf/10)==0:
                print "%s " %(idx+1)
    
            
            d_strechs=dict([(x, strechs[x]) for x in strech_list(sector, g1._subgraphs)])

            expr=decompose(sector_,[A1, A2 ] )+[poly_exp([[sector[0]]], (1, 0))]
            
#            print
#            print  "    sector ", sector_
#            print
#            print "   expr = ",  expr
#            print 
#            print "   expr = ",  poly_list2ccode(expr)
#            print
            
#            bp=find_bad_poly(expr)
#            print "    bp = ",  bp
#            print "    zeroes = ",  find_zeroes(bp[0][0])

#            print sector, g1._subgraphs
#            print "d_strechs", d_strechs
            terms=direct_subtraction((expr, {}), d_strechs, g1._tadpoles)
#            print
#            print "terms=", terms
#            print
            
            current_terms[sector_]=terms    

#perform additional decomposition for terms with a_i=0 (if necessary)

	    if second_decompose:
		current_terms,  sdsector_terms = split_sector_dict(current_terms)
        
#            print 
#            print sdsector_terms
###
                while len(sdsector_terms.keys())>0:
                    print "Bad sectors: ", len(sdsector_terms.keys())
                    sdsector_terms_=dict()
                    for sector in sdsector_terms:
                        terms=sdsector_terms[sector]
#                    print
#                    print sector
                        for term in  terms:
#                        print "---------"
#                        print "term = ", poly_list2ccode(term[0])
#                        print "term[1] = ", term[1]

                            bad_polys=find_bad_poly(term[0])
#                        print "bad_polys", bad_polys
                            if len(bad_polys)<>1:
                                raise NotImplementedError ,  " badpoly= %s, \nsector=%s,\n term=%s"%(bad_polys, sector, term)
                            else:
                                poly=bad_polys[0][0]
#                            print bad_polys[0]
                                a_=list(set(bad_polys[0][1]))
                            
                        
#                        print "a_", a_
                            if len(a_)==0:
#                            print poly
                                azeroes=find_zeroes(poly) 
                                zeroes=minimal_zeroes(azeroes  ,  nostrechs=True)
#                            print zeroes
#                            print "sector=", sector
                                sectors=list()
                                for u in zeroes[0]:
                                    vars=copy.copy(zeroes[0])
                                    vars.remove(u)
                                    new_sector=sect([u], [vars] )
#                                print "   new sector: ", new_sector
                                    d_term=(decompose(new_sector, term[0]), term[1])
#                                print "   d_term=",  poly_list2ccode(d_term[0])
                                    new_sector_=sector+new_sector
#                                active_strechs[new_sector_]=active_strechs[sector]
#                                print poly_list2ccode(d_term[0])
#                                print new_sector_    
                                    if new_sector_ not in sdsector_terms_:
                                        sdsector_terms_[new_sector_]=[]
                                    sdsector_terms_[new_sector_].append(d_term)
                            else:
                                if sector not in sdsector_terms_:
                                    sdsector_terms_[sector]=[]
                                d_strechs=dict([(x, strechs[x]) for x in a_])
                                sdsector_terms_[sector]+=direct_subtraction(term,  d_strechs, g1._tadpoles)
                            
                        
                    good_terms, sdsector_terms=split_sector_dict(sdsector_terms_)
                    current_terms=combine_dicts(current_terms,  good_terms)
                    print "saved:" , len(good_terms.keys())
#                print
            
###
            #print "Total sectors: ",  len(current_terms.keys())
#
            for sector in current_terms.keys():
                terms=current_terms[sector]
#            print "sector ",  sector
#            for term in terms:
#                print "   term[1] = ",  term[1]
#                print "   term = ",  poly_list2ccode(term[0])
                
            

                s_terms=[]
                for term in terms:
                    s_terms+=diff_subtraction(term, strechs)

                if len(s_terms)==0:
                    del current_terms[sector]
                else:
                    current_terms[sector]=s_terms
	    sector_terms=combine_dicts(sector_terms, current_terms)                    
	    
	    if len(sector_terms)>=Nf:
	        save_sectors(g1,sector_terms,strech_vars,name_,idx_save)
	        idx_save+=1
	        Nsaved+=len(sector_terms)
	        print "saved to file  %s sectors (%s) ..."%(Nsaved,idx_save)
	        sector_terms=dict()

	if len(sector_terms)>0:
	    save_sectors(g1,sector_terms,strech_vars,name_,idx_save)
	    idx_save+=1
	    Nsaved+=len(sector_terms)
	    print "saved to file  %s sectors (%s) ..."%(Nsaved,idx_save)
	    sector_terms=dict()
	f=open("tmp/%s.c"%(name_),'w')
        f.write(code(idx_save-1, len(g1._qi.keys())+len(strech_vars), "%s_func"%name_))
        f.close()


        
    




