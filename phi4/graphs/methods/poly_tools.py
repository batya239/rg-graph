#!/usr/bin/python
# -*- coding:utf8
import copy

class InvalidDecomposition(Exception):
    pass

class DivergencePresent(Exception):
    pass

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
        res=[]
        for i in range(len(self.poly)):
            monom=copy.copy(self.poly[i])
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
#                for i in range(monom.count(var)):
                monom_.remove(var)
                for i in range(monom.count(var)):
                    diff_.append(monom_)
        if len(diff_)==0:
            return []
        else:
            return [poly_exp(diff_,(1, 0), coef=self.power), poly_exp(res,self.power-1,self.degree, self.coef)]

    def GCD(self):
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
    for poly in poly_lst:
#        print var, poly
        poly_=poly.set0(var)
        if len(poly_.poly)>0:
            res.append(poly_)
        else:
            if poly_.power.a>=0:
                return []
            else:
                raise ZeroDivisionError,  "var:=%s poly=%s"%(var, poly)
    return res

def set1_poly_lst(poly_lst, var):
    res=[]
    for poly in poly_lst:
        res.append(poly.set1(var))
    return res

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
                continue
            else:
                res.append(poly)
                continue
        gcd=poly.GCD()
        if len(gcd.poly)==1:
            if len(gcd.poly[0])<>0:
                res.append(gcd)
                res.append(poly.extract(gcd.poly[0]))
            elif len(gcd.poly[0])==0:
                res.append(poly)
        else:
            raise Exception,  "GCD must be monomial, poly=%s, gcd=%s"%(poly, gcd)
        #    print "FACTORIZE",  res
    return res

def poly2str(poly):
    if len(poly)==0:
        return "1"
    else:
        res=""
        for monom in poly:
            res+="%s+"%monom2str(monom)
        return res[:-1]

def monom2str(monom):

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

def is1present(poly):
    for monom in poly:
        if len(monom)==0:
            return True
    return False

def poly_list2ccode(poly_list, check_bad_decompositions=True):
    res=""
    factor=dict()
    C=1.
    if len(poly_list)==0:
        return "0."
    for poly in poly_list:
        if len(poly.poly)==0:
            pass
        elif len(poly.poly)==1:
            for var in poly.poly[0]:
                if var not in factor:
                    factor[var]=exp_pow((0,0))
                factor[var]+=poly.power
        else:
            unitpresent=is1present(poly.poly)
            t_poly=poly2str(poly.poly)
            if poly.power.a==1:
                res+= "(%s)*"%(t_poly)
            elif poly.power.a==0:
                res+= "(1.)*"
            else:
                if check_bad_decompositions and (poly.power.a<0 and not unitpresent):
                    raise InvalidDecomposition, "polynom in negative power without 1 term"
                res+= "pow(%s,%s)*"%(t_poly, poly.power.a)
        C=C*poly.coef.a
    for var in factor.keys():
        power=factor[var]
        if power.a == 0:
            continue
        else:
            if power.a ==1:
                res+="(u%s)*"%(var)
            else:
                if check_bad_decompositions and power.a<0:
                    raise DivergencePresent, "Negative power of feynman parameter ==> divergence"
                res+="pow(u%s,%s)*"%(var,power.a)
    if C==1:
        return res[:-1]
    else:
        return "%s(%s)"%(res, C)