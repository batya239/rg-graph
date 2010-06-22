#!/usr/bin/python
# -*- coding: utf8
'''Generators for the combinations, permutations and selections.
'''

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



