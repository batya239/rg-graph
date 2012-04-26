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



def Prepare(graph, model):
    model.SetTypes(graph)
    model.checktadpoles=False
    graph.FindSubgraphs(model)
    
    subs_toremove=subgraphs.DetectSauseges(graph._subgraphs)
    graph.RemoveSubgaphs(subs_toremove)

    subgraphs.RemoveTadpoles(graph)
    
    int_edges=graph._internal_edges_dict()
    cons = conserv.Conservations(int_edges)
    eqs = find_eq(cons)
    print
    print cons, eqs
    cons=apply_eq(cons, eqs)
    print "Conservations:\n", cons
    graph._cons=cons
    graph._qi, graph._qi2l = qi_lambda(cons, eqs)
    print graph._qi, graph._qi2l
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
          res.append(copy.copy(monom)+factor)
       return poly_exp(res,self.power,self.degree,  self.coef)

    def extract(self,varlist):
#       print
       res=[]
       for i in range(len(self.poly)):
           
          monom=copy.deepcopy(self.poly[i])
#          print 
#          print i, res
#          print monom, varlist
          for var in varlist:
             monom.remove(var)
          res.append(monom)
       return poly_exp(res,self.power,self.degree, self.coef)
       
    def set0(self, var):
        res=[]
        for monom in self.poly:
            if var not in monom:
                res.append(copy.copy(monom))
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
                poly_lst_.append(copy.deepcopy(poly2))
        
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
                raise ZeroDivisionError,  "var:=%s poly="%(var, poly)
    return res
    
def set1_poly_lst(poly_lst, var):
    res=[]
    for poly in poly_lst:
        res.append(poly.set1(var))
    return res


def decompose(sector, poly_lst):
#    print sector, poly_lst
    res = [copy.deepcopy(x) for x in poly_lst]
    used_vars = []
    extracted=dict()
    for var in sector.sect:
        sector_idx=sector.sect.index(var)
        v_vars = sector.var[sector_idx]

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
#                print var
                poly=poly.extract([var,]*(poly.degree-sector_idx))
#                print poly
#                print
            res_n.append(poly)
        res=res_n

#        print "\n ---\n %s \n ---\n"%res

     
    for poly in extracted.values():
       res.append(poly)
                
    return res

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

def functions(poly_dict,vars,  strechs):
    res2="""
void func(double k[DIMENSION], double f[FUNCTIONS])
{
f[0]=0.;
"""
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
double func%s( %s)
{
//sector %s
"""%(cnt,varstring,sector)
        cnt2=0
        
        s0="1./(1.+"
        for var in vars+strechs:
            if var<>sector.sect[0]:
                res+="double u%s=w_%s;\n"%(var,cnt2)
                cnt2+=1
        
        

        expr, subs=poly_dict[sector]
        res+="double u%s=1./(1.+%s);\n"%(sector.sect[0],subs)
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
    

def check_comb(term, cons):
    res=True
    for constr in cons:
        if constr.issubset(term):
            res=False
            break
    return res
    
    
def strech_list(term, subgraphs_):
    strechs=[]
    subs=conv_sub(subgraphs_)
    for j in range(len(subs)):
        si=len(set(term)&set(subs[j]))-subgraphs_[j].NLoopSub()
        strechs+=[1000+j]*si
    return strechs


def gensectors(cons,vars, L):
    sect=[]
    for i in xCombinations(vars.keys(), L):
        if check_comb(i, cons):
            sect.append(i)            
    return sect

"""
        for i in range(len(subs)):
            si=len(set(term)&set(subs[i]))-subgraphs_[i].NLoopSub()
            if si>0:
                ai=sympy.var('a_%s'%subgraphs_[i].asLinesIdxStr())
                sterm*=ai**si
                subgraphs_[i]._strechvar=str(ai)
"""
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


def split_sector_dict(sector_terms):
    good_terms=dict()
    bad_terms=dict()
    for sector in sector_terms:
        good_terms[sector]=[]
        bad_terms[sector]=[]
        for term in sector_terms[sector]:
            term_=factorize_poly_lst(term)
            sd_required=False
            for poly in term_:
                if poly.power.a<0 and len(poly.poly)>1:
                    if min(map(len, poly.poly))<>0:
                        sd_required=True
            if sd_required:
                bad_terms[sector].append(term_)
            else:
                good_terms[sector].append(term_)
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
        
    


def save_sd(name, g1,  model):
    print g1._eq_grp
    for grp_ in g1._eq_grp:
        if len(grp_)==0:
            continue
        print grp_  ,  g1._qi, list(set(grp_)& set(g1._qi))
        qi=list(set(grp_)&set(g1._qi))[0]
        name_="%s_%s_"%(name, qi)
        ui=reduce(lambda x, y:x+y,  [[qi_]*(g1._qi[qi_]-1) for qi_ in g1._qi])
    #    print ui
#        qi=g1._qi.keys()[0]
        ui.append(qi)
        print "   term u%s"%qi
        print ui,  g1._eq_grp
        for sub in g1._subgraphs:
            sub._strechvar=1000+g1._subgraphs.index(sub)
    
        lfactor=1.
        for qi_ in g1._qi.keys():
            if qi_==qi:
                lfactor=lfactor/sympy.factorial(g1._qi[qi_])
            else:
                lfactor=lfactor/sympy.factorial(g1._qi[qi_]-1)
    
        
        grp=None
        for grp in g1._eq_grp:
            if qi in grp:
                break
        grp_factor=len(grp)
    
    #    print lfactor, g1.sym_coef(), grp_factor 
    
        A1=poly_exp(g1._det, (-2, 0), g1.NLoops(), coef=(float(lfactor*g1.sym_coef()*grp_factor ), 0))
#        print "DET=", A1
#        print "DET0=", set0_poly_lst([A1], 1000)
        A2=poly_exp([ui, ], (1, 0))
        A3=poly_exp([g1._qi.keys()], (1, 0))
        A4=poly_exp([g1._qi.keys()], (-1, 0))
        g_qi=dTau_line(g1, qi,  model)
        strechs=strech_indexes(g_qi, model)
        #print [A1, A2, A3 ]
        
        strech_vars=[]
        for var in strechs:
            if strechs[var]>0:
                strech_vars.append(var)
                
        Nf=100
        sect_terms=dict()
#        g1._sectors=[[6, 7, 10, 12, 8]]
        sector_terms=dict()
        for sector in g1._sectors:
            vars_lst=[]
            used_vars=[]
            for var in sector:
                used_vars.append(var)
                vars_lst.append( valid_vars(sector, used_vars, g1._qi, g1._cons))
            sector_=sect(sector, vars_lst)
            print sector_
            
            
            idx=g1._sectors.index(sector)
            if (idx+1) % (Nf/10)==0:
                print "%s " %(idx+1)
    
            
            active_strechs=strech_list(sector, g1._subgraphs)



            expr=decompose(sector_,[A1, A2, A3 ] )+[A4]+[poly_exp([[sector[0]]], (1, 0))]

            terms=[expr]
            
#            ttt = decompose(sector,[A1 ], g1._qi,  g1._cons )
#            print sector, ttt

            for var in strechs:

                terms_=[]
                if strechs[var]==0:
                    for term in terms:
                        terms_.append(set1_poly_lst(term, var))
                elif strechs[var]==1:
                    for term in terms:

                        if var not in active_strechs:
                            terms_+=diff_poly_lst(term, var)
                        else:
                            terms_.append(minus(set0_poly_lst(term, var)))
                            terms_.append(set1_poly_lst(term, var))
                elif strechs[var]==2:
                    for term in terms:
                        firstD=diff_poly_lst(term, var)
                        if var not in active_strechs: 
#                            print var, term
                            for term_ in firstD:
                                seconD=diff_poly_lst(term_, var)
                                for term__ in seconD:
#не работает если переменная имеет индекс 0                                    
                                    term__.append(poly_exp([[], [-var]], (1, 0)))
                                    terms_+=[term__]
                        else:
                            terms_.append(set1_poly_lst(term, var))
                            terms_.append(minus(set0_poly_lst(term, var)))
                            for term_ in firstD:
                                terms_.append(minus(set0_poly_lst(term_, var)))
                else:
                    raise NotImplementedError,  "strech level   = %s"%strechs[var]

                terms=terms_
            sector_terms[sector_]=terms    
        
#        print [(sector, len(sector_terms[sector])) for sector in sector_terms.keys()]
        #perform additional decomposition for terms with a_i=0 (if necessary)
        
        
        sector_terms2,  sdsector_terms = split_sector_dict(sector_terms)
        sector_terms2,  sdsector_terms = split_sector_dict(sector_terms)
        while False and len(sdsector_terms.keys())>0:
            decomposed=dict()
            for sector in sdsector_terms:
                terms=sdsector_terms[sector]
                v_vars = sector.var[-1]
#                print
#                print sector,  v_vars
#                for term in  terms:
#                    print term

        
#        print sdsector_terms.keys()

        
        
        
        for sector in sector_terms.keys():
            subs=[[x] for x in g1._qi.keys()]
            subs.remove([sector.sect[0]])
            

            subs_polyl=decompose(sect(sector.sect[1:], sector.var[1:]), [poly_exp(subs,  (1, 0))] )
#            print subs_polyl, poly_list2ccode(subs_polyl)
            terms=sector_terms[sector]
            tres=""
            for term in   terms:
                f_term=factorize_poly_lst(term)
                tres+="%s;\nres+="%poly_list2ccode(f_term)
            sect_terms[sector]=(tres[:-5], poly_list2ccode(subs_polyl))
#            print (tres[:-5], poly_list2ccode(subs_polyl))
            if (idx+1) % Nf==0:
                if len(sect_terms)<>0:
                    print
                    print "write to disk... %s"%(idx+1)
                    f=open("tmp/%s%s.c"%(name_,idx/Nf),'w')
                    f.write(code(functions(sect_terms, g1._qi.keys(), strech_vars), len(g1._qi.keys())+len(strech_vars)))
                    f.close()
                    sect_terms=dict()
    
        if len(sect_terms)<>0:
            print "write to disk... %s"%(idx+1)
            f=open("tmp/%s%s.c"%(name_,idx/Nf),'w')
            f.write(code(functions(sect_terms, g1._qi.keys(), strech_vars), len(g1._qi.keys())+len(strech_vars)))
            f.close()
            sect_terms=dict()
    



"""
det=gendet(cons,N,L)
sect=gensectors(cons,N,L)
print len(det)
#print sect
print len(sect)
print "//det generated"

det_p=poly_exp(det,(-2,0),L)
u_p=poly_exp([range(N)],(1,0))
u_mp=poly_exp([range(N)],(-1,0))

sect_expr=dict()

Nf=1000


for sector in sect:
    idx=sect.index(sector)
    if (idx+1) % Nf == 0:
        print "write to disk... %s"%(idx+1)
        f=open("%s%s.c"%(name,idx/Nf),'w')
        f.write(code(functions(sect_expr, N), N))
        f.close()
        sect_expr=dict()

    sys.stdout.flush()
    poly_list = decompose(sector,[det_p,u_p],N,cons) + [u_mp]
    sect_expr[tuple(sector)] = poly_list2ccode(poly_list+[poly_exp([[sector[0]]],(1,0))])

if len(sect_expr)<>0:
    print "write to disk... %s"%(idx+1)
    f=open("%s%s.c"%(name,idx/Nf),'w')
    f.write(code(functions(sect_expr, N), N))
    f.close()
    sect_expr=dict()
 

"""
    







