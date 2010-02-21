#!/usr/bin/python
# -*- coding: utf8

'''
Created on Feb 20, 2010

@author: mkompan
'''
#Common generators

from sympy import *

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

def UniqueSelections(items,n):
    lst = [i for i in xSelections(items,n)]
    print lst
    for idx in lst:
        idx.sort()
        print idx
    print lst
    return list(set(lst))

        

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

def SimpleSeries(func,var,point,num):
    level=0
    flag=1
    f=func
    res=0
    while(flag>0):
        tmp=limit(abs(f),var,point) 
        if type(tmp)==core.numbers.Infinity :
            level=level-1
            f=f*(var-point)
        else:
            if level<=num :
                res=limit(f,var,point)*pow(var-point,level)
            else:
                res=0
            flag=0

    N=1
    for i in range(level,num):
        f=expand(f.diff(var)/N)
        N=N+1
        res=res+limit(expand(f),var,point)*pow(var-point,i+1)

    return res

