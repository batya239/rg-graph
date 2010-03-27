#!/usr/bin/python
# -*- coding: utf8

'''
Created on Feb 20, 2010

@author: mkompan
'''
#Common generators


#from sympy import *
import sympy
import time
import sys

def xSelections(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for ss in xSelections(items, n-1):
                yield [items[i]]+ss

def xUniqueSelections(items, n):
    ''' Selections where [1,2] = [2,1]
    '''
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for ss in xUniqueSelections(items[i:], n-1):
                yield [items[i]]+ss

#def UniqueSelections(items,n):
#    lst = [i for i in xSelections(items,n)]
#    print lst
#    for idx in lst:
#        idx.sort()
#        print idx
#    print lst
#    return list(set(lst))

        

def xCombinations(seq, n):
    """Generator of all the n-element combinations of the given sequence.
    """
    if n == 0:
        yield seq[0:0]
    else:
        for i in range(len(seq)):
            for tail in xCombinations(seq[:i] + seq[i+1:], n - 1):
                yield seq[i:i+1] + tail


def xPermutations(seq):
    """Generator of all the permutations of the given sequence.
    """
    return xCombinations(seq, len(seq))

def xUniqueCombinations(items, n):
    if n==0: yield []
    else:
        for i in xrange(len(items)):
            for cc in xUniqueCombinations(items[i+1:],n-1):
                yield [items[i]]+cc


def SimpleSeries(func,var,point,num):
# TODO: doesnt work sometimes.
    
    level=0
    flag=1
    if 'series' in dir(func):
        f=func.series(var,point=point,n=num+2)
    else:
        f=func
    try:    
        for OO in f.atoms(sympy.Order):
            f=f.subs(OO,0)
    except  AttributeError:
        pass
    res=0
    while(flag>0):
        tmp=sympy.limit(abs(f),var,point) 
        if type(tmp)==sympy.core.numbers.Infinity :
            level=level-1
            f=f*(var-point)
        else:
            if level<=num :
                res=sympy.limit(f,var,point)*pow(var-point,level)
            else:
                res=0
            flag=0

    N=1
    for i in range(level,num):
        f=sympy.expand(sympy.diff(f,var)/N)
        N=N+1
        res=res+sympy.limit(sympy.expand(f),var,point)*pow(var-point,i+1)

    return res

def print_time(str_, debug=True):
    if debug:
        print "\t\t\t time (%s) = %s"%(str_,time.time())
        sys.stdout.flush()
        
def print_debug(str_, debug=True):
    if debug:
        print str_
        sys.stdout.flush()


def RelativeError(expr, err, var):
    t_expr = expr
    t_err = err
    res = dict()
    idx = 0
    while(t_expr<>0):
        res[idx] = (t_err.subs(var,0),t_err.subs(var,0)/t_expr.subs(var,0))
        idx = idx + 1
        t_expr = t_expr.diff(var)/idx
        t_err = t_err.diff(var)/idx
    return res    
    
    
