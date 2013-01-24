#!/usr/bin/python
# -*- coding: utf8 -*-

from utils.numbers import Number, Series, sympyseries_to_list
import math
import copy

minerr = 10 ** -20
minerr = 0
import sys

if len(sys.argv) == 3:
    max_err = -int(sys.argv[2])
else:
    max_err = -3

table = eval(open(sys.argv[1]).read())
table['ee11-22-ee-'] = [[0, ], [minerr, ]]
table['ee11-22-33-ee-'] = [[0, ], [minerr, ]]
table['ee11-23-e33-e-'] = [[0, ], [minerr, ]]
table['ee11-22-33-44-ee-'] = [[0, ], [minerr, ]]
table['ee11-22-34-e44-e-'] = [[0, ], [minerr, ]]
table['e112-e2-34-e44-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e44-e44--'] = [[0, ], [minerr, ]]
table['ee11-23-ee4-444--'] = [[0, ], [minerr, ]]
table['ee11-23-e34-44-e-'] = [[0, ], [minerr, ]]
table['ee11-23-334-4-ee-'] = [[0, ], [minerr, ]]
table['ee11-23-345-45-e5-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e34-45-55-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e45-445-5-e-'] = [[0, ], [minerr, ]]
table['ee11-23-445-455-e-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e44-e55-55--'] = [[0, ], [minerr, ]]
table['ee11-22-34-e55-e55--'] = [[0, ], [minerr, ]]
table['ee11-23-445-445--ee-'] = [[0, ], [minerr, ]]
table['ee11-22-34-e45-55-e-'] = [[0, ], [minerr, ]]
table['ee11-23-344-45-5-ee-'] = [[0, ], [minerr, ]]
table['ee11-23-344-55-e5-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e44-455-5-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e34-55-e55--'] = [[0, ], [minerr, ]]
table['ee11-23-334-5-e55-e-'] = [[0, ], [minerr, ]]
table['ee11-23-e45-e45-55--'] = [[0, ], [minerr, ]]
table['e112-e2-34-e55-e55--'] = [[0, ], [minerr, ]]
table['e112-e2-34-e45-55-e-'] = [[0, ], [minerr, ]]
table['ee11-22-33-44-55-ee-'] = [[0, ], [minerr, ]]
table['ee11-22-33-45-e55-e-'] = [[0, ], [minerr, ]]
table['ee11-22-34-445-5-ee-'] = [[0, ], [minerr, ]]
table['ee11-23-334-4-55-ee-'] = [[0, ], [minerr, ]]
table['e112-e2-33-45-e55-e-'] = [[0, ], [minerr, ]]
table['ee12-223-3-45-e55-e-'] = [[0, ], [minerr, ]]
table['ee12-223-3-45-e55-e-'] = [[0, ], [minerr, ]]

f_ = dict() #for graph summs


def sum(n_list, table):
    res = []
    err = []
    for term in n_list:
        coef, nomen = term
        for i in range(len(table[nomen])):
            if len(res) > i:
                res[i] += coef * table[nomen]


import kleinert

import sympy
from graphs import Graph

zeta = lambda x: sympy.special.zeta_functions.zeta(x).evalf()


def f(nomenkl):
    if not table.has_key(nomenkl):
        if not f_.has_key(nomenkl):
            raise ValueError, "no such graph in table: %s" % nomenkl
        else:
            return f_[nomenkl]
    g = Graph(nomenkl)
    g.GenerateNickel()
    res = list()
    num, err = table[nomenkl]
    for i in range(len(num)):
        res += [(Number(num[i] / g.sym_coef(), err[i] / g.sym_coef()), i)]
    return Series(res)


def K_ms(expr):
    return expr.series(0)


def K(expr, N=1000):
    return expr.series(N)


def printKR1(key):
    e = sympy.var('e')
    res = 0
    bad = False
    if isinstance(key, tuple):
        for t_ in key:
            coef, g_ = t_
            if g_ in kleinert.MS.keys():
                res += coef * kleinert.MS[g_].evalf()
            else:
                bad = True
                #                print bad, g_
        key_ = str(key)
    elif key in kleinert.MS.keys():
        res = kleinert.MS[key].evalf()
        key_ = key
    else:
        bad = True

    print key_
    print "   ", KR1_ms[key_].sympy_series()

    if not bad:
        print "   ", res
        print
        print "   ", (KR1_ms[key_].sympy_err_series()), "  #my"
        tdif = (KR1_ms[key_].sympy_series() - res).series(e, 0, 10000)
        print "   ", tdif, "   #difference"
        if tdif <> 0:
            aa = int(math.log10(max(map(abs, [x[0] for x in sympyseries_to_list(tdif, e, start=-6)]))))
            print "   MAX_ERR_POW=", aa,
            if aa >= max_err:
                print "  WARN"
            else:
                print
        else:
            print "   ", "-10000"

    print "      KR1 =  ", K(KR1[str(key)], 4).sympy_series()
    print "    R1_ms =  ", K(R1_ms[str(key)], 4).sympy_series()
    print "---------------------------------"
    print


def KR(gamma, R1op, R2op, nloops):
    e1 = Series([(Number(1, minerr), -1)]) # 1/e
    if isinstance(gamma, tuple):
        kr1 = 0
        for t_ in gamma:
            coef, gamma_ = t_
            kr1 += coef * f(gamma_)
        f_[str(gamma)] = kr1

    else:
        kr1 = f(gamma)
        #        print kr1
    print
    for r1term in R1op:
        coef, g, subs = r1term

        if len(subs) == 1:
            kr1 -= coef * KR1[g] * f(subs[0])
            print coef,g,subs[0]
            print coef * KR1[g] * f(subs[0])
    kr1 = K(kr1 * 2 / nloops * e1)
    print

    r1_ms = kr1
    g_ = kr1
    for r2term in R2op:
        r1_ms_term = 1.
        kr1_term = 1.
        coef, g, subs = r2term
        if len(subs) == 0:
            raise Exception, "no subgraphs in R1op:" % R1op

        #        print r2term
        for sub in subs:
            r1_ms_term = r1_ms_term * (R1_ms[sub] - KR1_ms[sub])
        r1_ms += coef * KR1[g] * r1_ms_term
        print " g ", g, KR1[g].sympy_series()
        print " sub_res ", subs, "\n   ", map(lambda x: K(R1_ms[x] - KR1_ms[x],3).sympy_series(), subs),"\n   ", K_ms(coef * KR1[g] * r1_ms_term).sympy_series()

    kr1_ms = K_ms(r1_ms)
    #    print kr1_ms
    KR1[str(gamma)] = kr1
    KR1_ms[str(gamma)] = kr1_ms
    R1_ms[str(gamma)] = r1_ms

e = sympy.var('e')
G = dict()
KR1 = dict()
R1_ms = dict()
KR1_ms = dict()

#4x 1loop 1
gamma = 'ee11-ee-'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 1)
printKR1(gamma)

#2x 2loop 1
gamma = 'e111-e-'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 2)
printKR1(gamma)

#4x 2loop 1
gamma = 'ee11-22-ee-'
R1op = [
    (2, 'ee11-ee-', ('ee11-ee-',)),
]
R2op = [
    (2, 'ee11-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 2)
printKR1(gamma)

#4x 2loop 2
gamma = 'ee12-e22-e-'
R1op = [
    (1, 'ee11-ee-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 2)
printKR1(gamma)

#2x 3loop 1
gamma = 'e112-22-e-'
R1op = [
    (2, 'e111-e-', ('ee11-ee-',)),
]
R2op = [
    (2, 'e111-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 1
gamma = 'ee11-22-33-ee-'
R1op = [
    (2, 'ee11-ee-', ('ee11-22-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-ee-')),
    (3, 'ee11-22-ee-', ('ee11-ee-',)),
]
R2op = [
    (2, 'ee11-ee-', ('ee11-22-ee-',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee11-ee-')),
    (3, 'ee11-22-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 2
gamma = 'ee11-23-e33-e-'
R1op = [
    (1, 'ee11-ee-', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-ee-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-ee-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

G['ee11-ee-'] = KR1['ee11-ee-']
G['ee11-ee-_1'] = sympy.Number(1) / 2 * f('ee11-ee-')
G['ee11-ee-_'] = f('ee11-ee-')
G['ee11-ee-_1k'] = G['ee11-ee-'] - G['ee11-ee-_1']
G['ee11-ee-_k'] = 2 * G['ee11-ee-'] - G['ee11-ee-_']
KR1['ee11-ee-_1'] = G['ee11-ee-_1']
KR1['ee12-ee2--'] = G['ee11-ee-_1']
KR1['ee11-ee-_'] = G['ee11-ee-_']
KR1['ee11-ee-_1k'] = G['ee11-ee-_1k']
KR1['ee11-ee-_k'] = G['ee11-ee-_k']

C1_ = Series([[Number(1, 0), -1]])
R1_ms['e111-e-_tau'] = 2 * f('ee12-e22-e-') * C1_
KR1_ms['e111-e-_tau'] = K_ms(R1_ms['e111-e-_tau'])
print R1_ms['e111-e-_tau']-KR1_ms['e111-e-_tau']

G['ee12-e22-e-'] = K( KR1['ee12-e22-e-']+G['ee11-ee-']*KR1['ee11-ee-'])
G['e111-e-_tau'] = K(-3*Series([[Number(1, 0), 0], [Number(1, 0), 1],
                                [Number(1, 0), 2], [Number(1, 0), 3],
                                [Number(1, 0), 4], [Number(1, 0), 5],
                                [Number(1, 0), 6]]) * G['ee12-e22-e-'])
G['ee0-'] = K(-Series([[Number(1, 0), 0], [Number(0.5, 0), 1],
                      [Number(0.25, 0), 2], [Number(0.125, 0), 3],
                      [Number(0.0625, 0), 4], [Number(0.03125, 0), 5],
                      [Number(0.015625, 0), 6]]) * G['ee11-ee-'])
R1_ms['e111-e-_tau'] = K(G['e111-e-_tau'] - 3 * G['ee0-'] * KR1_ms['ee11-ee-'])
KR1_ms['e111-e-_tau'] = K_ms(R1_ms['e111-e-_tau'])
print R1_ms['e111-e-_tau']-KR1_ms['e111-e-_tau']
print G['ee0-']
print G['e111-e-_tau']
print R1_ms['e111-e-_tau']
print "!-----------!--------!-------\n\n\n"

R1_ms['e111-e-_tau'] = Series([[Number(0, 0), 0],])
KR1_ms['e111-e-_tau'] = K_ms(R1_ms['e111-e-_tau'])


#4x 3loop 3
gamma = 'ee12-ee3-333--'
R1op = [
    (1, 'ee11-ee-_1k', ('e111-e-',)),
]
R2op = [
    (1, 'ee12-ee2--', ('e111-e-_tau',)),
    (1, 'ee11-ee-_1k', ('e111-e-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 4
gamma = 'e123-e23-e3-e-'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 5
gamma = 'ee12-e33-e33--'
R1op = [
    (1, 'ee11-ee-', ('ee11-22-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee11-22-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 6
gamma = 'e112-e3-e33-e-'
R1op = [
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e22-e-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e22-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 7
gamma = 'ee12-e23-33-e-'
R1op = [
    (1, 'ee11-ee-', ('ee12-e22-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee12-e22-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 3loop 8
gamma = 'ee12-223-3-ee-'
R1op = [
    (2, 'ee11-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-',)),
]
R2op = [
    (2, 'ee11-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 3)
printKR1(gamma)

#4x 4loop 1
gamma = 'ee11-22-33-44-ee-'
R1op = [
    (-3, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (4, 'ee11-22-33-ee-', ('ee11-ee-',)),
    (3, 'ee11-22-ee-', ('ee11-22-ee-',)),
    (2, 'ee11-ee-', ('ee11-22-33-ee-',)),
    (-2, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
R2op = [
    (3, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (4, 'ee11-22-33-ee-', ('ee11-ee-',)),
    (3, 'ee11-22-ee-', ('ee11-22-ee-',)),
    (2, 'ee11-ee-', ('ee11-22-33-ee-',)),
    (2, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 2
gamma = 'ee11-22-34-e44-e-'
R1op = [
    (2, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee11-23-e33-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-33-ee-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee12-e22-e-', ('ee11-22-ee-',)),
]
R2op = [
    (2, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee11-23-e33-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-33-ee-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee12-e22-e-', ('ee11-22-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 3
gamma = 'e112-e2-34-e44-e-'
R1op = [
    (2, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (-2, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
]
R2op = [
    (2, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (2, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 4
gamma = 'ee11-23-e44-e44--'
R1op = [
    (2, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-22-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-e33--',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
R2op = [
    (2, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-22-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-e33--',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

G['ee11-22-ee-_1'] = K(G['ee11-ee-'] * G['ee11-ee-_1'])  # K(G['ee11-22-ee-']-G['ee11-ee-']*G['ee11-ee-_1'])
G['ee11-22-ee-_1k'] = K(G['ee11-ee-'] * G['ee11-ee-_1k'])  # K(G['ee11-22-ee-']-G['ee11-ee-']*G['ee11-ee-_1'])
KR1['ee11-22-ee-_1k'] = K(G['ee11-22-ee-_1k'] - G['ee11-ee-'] * KR1['ee11-ee-_1k'] - G['ee11-ee-_1k'] * KR1['ee11-ee-'])
KR1['ee11-22-ee-_1'] = K(G['ee11-22-ee-_1'] - G['ee11-ee-_1'] * KR1['ee11-ee-'] - G['ee11-ee-'] * KR1['ee11-ee-_1'])
#4x 4loop 5
gamma = 'ee11-23-ee4-444--'
R1op = [
    (1, 'ee11-22-ee-_1k', ('e111-e-',)),
    (-1, 'ee11-ee-_1k', ('ee11-ee-', 'e111-e-')),
    (1, 'ee11-ee-', ('ee12-ee3-333--',)),
    (1, 'ee12-ee3-333--', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-22-ee-_1k', ('e111-e-',)),
    (1, 'ee11-22-ee-_1', ('e111-e-_tau',)),
    (1, 'ee11-ee-', ('ee12-ee3-333--',)),
    (1, 'ee11-ee-_1k', ('ee11-ee-', 'e111-e-')),
    (1, 'ee11-ee-_1', ('ee11-ee-', 'e111-e-_tau')),
    (1, 'ee12-ee3-333--', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 6
gamma = 'ee11-23-e34-44-e-'
R1op = [
    (1, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e22-e-',)),
]
R2op = [
    (1, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 7
gamma = 'ee11-23-334-4-ee-'
R1op = [
    (1, 'ee11-ee-', ('ee12-223-3-ee-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'ee11-22-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-33-ee-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee11-23-e33-e-',)),
    (1, 'ee12-223-3-ee-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee12-223-3-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'ee11-22-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-33-ee-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee11-23-e33-e-',)),
    (1, 'ee12-223-3-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 8
gamma = 'ee12-233-34-4-ee-'
R1op = [
    (2, 'ee11-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e22-e-',)),
    (1, 'ee12-223-3-ee-', ('ee11-ee-',)),
]
R2op = [
    (2, 'ee11-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e22-e-',)),
    (1, 'ee12-223-3-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 9
gamma = 'ee12-223-4-e44-e-'
R1op = [
    (1, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e33-e-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-223-3-ee-', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-23-e33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e33-e-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-223-3-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 10
gamma = 'e123-e24-34-e4-e-'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 11
gamma = 'e112-34-e34-e4-e-'
R1op = [
    (1, 'e123-e23-e3-e-', ('ee11-ee-',)),
]
R2op = [
    (1, 'e123-e23-e3-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 12
gamma = 'e112-e3-e34-44-e-'
R1op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'e112-e3-e33-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
]
R2op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'e112-e3-e33-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 13
gamma = 'e112-e3-e44-e44--'
R1op = [
    (2, 'e112-e3-e33-e-', ('ee11-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-22-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
R2op = [
    (2, 'e112-e3-e33-e-', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-22-ee-',)),
    (1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

#4x 4loop 14
gamma = 'ee12-334-334--ee-'
R1op = [
    (1, 'ee11-22-ee-', ('ee11-22-ee-',)),
    (2, 'ee12-223-3-ee-', ('ee11-ee-',)),
    (2, 'ee11-ee-', ('ee12-e33-e33--',)),
]
R2op = [
    (1, 'ee11-22-ee-', ('ee11-22-ee-',)),
    (2, 'ee12-223-3-ee-', ('ee11-ee-',)),
    (2, 'ee11-ee-', ('ee12-e33-e33--',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

R1_ms['e112-22-e-_tau'] = K(4 * (R1_ms['ee12-e23-33-e-'] + G['ee11-ee-'] * KR1_ms['ee12-e22-e-']) +
                            (R1_ms['ee12-e33-e33--'] + G['ee11-ee-'] * KR1_ms['ee11-22-ee-']))

R1_ms['e112-22-e-_tau'] = K(Series([[Number(0, 0), 0],]))
KR1_ms['e112-22-e-_tau'] = K_ms(R1_ms['e112-22-e-_tau'])



#4x 4loop 15
gamma = 'ee12-ee3-344-44--'
R1op = [
    (1, 'ee11-ee-_1k', ('e112-22-e-',)),
    (2, 'ee12-ee3-333--', ('ee11-ee-',)),
]
R2op = [
    (1, 'ee11-ee-_1k', ('e112-22-e-',)),
    (1, 'ee11-ee-_1', ('e112-22-e-_tau',)),
    (2, 'ee12-ee3-333--', ('ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

G['ee12-e22-e-'] = K(KR1['ee12-e22-e-'] + G['ee11-ee-'] * KR1['ee11-ee-'])
G['ee12-e22-e-_'] = K(f('ee12-e22-e-') + f('ee11-ee-') * KR1['ee11-ee-'])
G['ee12-e22-e-_k'] = K(4 * G['ee12-e22-e-'] - G['ee12-e22-e-_'])
KR1['ee12-e22-e-_k'] = K(G['ee12-e22-e-_k'] - G['ee11-ee-'] * KR1['ee11-ee-_k'] - G['ee11-ee-_k'] * KR1['ee11-ee-'])
KR1['ee12-e22-e-_'] = K(G['ee12-e22-e-_'] - G['ee11-ee-'] * KR1['ee11-ee-_'] - G['ee11-ee-_'] * KR1['ee11-ee-'])


print "\n\n\n\n=================\n==============="
print K(KR1['ee12-e22-e-_k']+KR1['ee12-e22-e-_']).sympy_series()
print K(KR1['ee12-e22-e-_']).sympy_series()
print K(4*KR1['ee12-e22-e-']).sympy_series()

print "16+19"
#4x 4loop 16+19
gamma = (
    (2, 'ee12-e23-e4-444--'),
    (2, 'ee12-e33-444-e4--'),
)
R1op = [
    (1, 'ee12-e22-e-_k', ('e111-e-',)),
    (2, 'ee11-ee-', ('ee12-ee3-333--',)),
    (2, 'ee12-ee3-333--', ('ee11-ee-',)),
    (-1, 'ee11-ee-_k', ('ee11-ee-', 'e111-e-',)),
]

R2op = [
    (1, 'ee12-e22-e-_k', ('e111-e-',)),
    (1, 'ee12-e22-e-_', ('e111-e-_tau',)),
    (2, 'ee11-ee-', ('ee12-ee3-333--',)),
    (2, 'ee12-ee3-333--', ('ee11-ee-',)),
    (1, 'ee11-ee-_k', ('ee11-ee-', 'e111-e-',)),
    (1, 'ee11-ee-_', ('ee11-ee-', 'e111-e-_tau',)),
]

KR(gamma, R1op, R2op, 4)
printKR1(gamma)


#4x 4loop 17
gamma = 'ee12-e34-e34-44--'
R1op = [
    (1, 'ee11-ee-', ('ee12-223-3-ee-',)),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee12-e22-e-',)),
]
R2op = [
    (1, 'ee11-ee-', ('ee12-223-3-ee-',)),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "18"
#4x 4loop 18
gamma = 'ee12-e33-e44-44--'
R1op = [
    (1, 'ee11-ee-', ('ee11-22-33-ee-',)),
    (3, 'ee12-e33-e33--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-22-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
R2op = [
    (1, 'ee11-ee-', ('ee11-22-33-ee-',)),
    (3, 'ee12-e33-e33--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "20"
#4x 4loop 20
gamma = 'ee12-233-44-e4-e-'
R1op = [
    (2, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e33-e-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]

R2op = [
    (2, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e33-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "21"
#4x 4loop 21
gamma = 'ee12-234-34-e4-e-'
R1op = [
    (1, 'ee11-ee-', ('e123-e23-e3-e-',)),
]
R2op = [
    (1, 'ee11-ee-', ('e123-e23-e3-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "22"
#4x 4loop 22
gamma = 'ee12-334-344-e-e-'
R1op = [
    (2, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e33-e-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
R2op = [
    (2, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e33-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "23"
#4x 4loop 23
gamma = 'ee12-e33-344-4-e-'
R1op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee11-23-e33-e-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
R2op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e33-e33--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee11-23-e33-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "24"
#4x 4loop 24
gamma = 'ee12-e23-44-e44--'
R1op = [
    (2, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-e33--',)),
    (1, 'ee12-e22-e-', ('ee11-22-ee-',)),
]
R2op = [
    (2, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-e33--',)),
    (1, 'ee12-e22-e-', ('ee11-22-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "25"
#4x 4loop 25
gamma = 'ee12-e34-334-4-e-'
R1op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee12-e23-33-e-',)),
]
R2op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee12-e23-33-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "26"
#4x 4loop 26
gamma = 'ee12-e23-34-44-e-'
R1op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee12-e23-33-e-',)),
]
R2op = [
    (1, 'ee12-e23-33-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee12-e23-33-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "2x 4loop 1"
#2x 4loop 1
gamma = 'e112-33-e33--'
R1op = [
    (3, 'e112-22-e-', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee11-22-ee-',)),
    (-1, 'e111-e-', ('ee11-ee-', 'ee11-ee-')),
]
R2op = [
    (3, 'e112-22-e-', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee11-22-ee-',)),
    (1, 'e111-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

G['e111-e-'] = KR1['e111-e-']
G['e111-e-_1'] = sympy.Number(1) / 3 * f('e111-e-')
G['e111-e-_'] = f('e111-e-')
G['e111-e-_1k'] = K(G['e111-e-'] - G['e111-e-_1'])
G['e111-e-_k'] = K(3 * G['e111-e-'] - G['e111-e-_'])
KR1['e111-e-_1k'] = K(G['e111-e-_1k'])
KR1['e111-e-_k'] = K(G['e111-e-_k'])
KR1['e111-e-_1'] = K(G['e111-e-_1'])
KR1['e111-e-_'] = K(G['e111-e-_'])

print "2x 4loop 2"
#2x 4loop 2
gamma = 'e112-e3-333--'
R1op = [
    (1, 'e111-e-_1k', ('e111-e-',)),
]
R2op = [
    (1, 'e111-e-_1k', ('e111-e-',)),
    (1, 'e111-e-_1', ('e111-e-_tau',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "2x 4loop 3"
#2x 4loop 3
gamma = 'e123-e23-33--'
R1op = [
    (1, 'e112-22-e-', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee12-e22-e-',)),
]
R2op = [
    (1, 'e112-22-e-', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "2x 4loop 4"
#2x 4loop 4
gamma = 'e112-23-33-e-'
R1op = [
    (2, 'e112-22-e-', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee12-e22-e-',)),
    (-1, 'e111-e-', ('ee11-ee-', 'ee11-ee-',)),
]
R2op = [
    (2, 'e112-22-e-', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee12-e22-e-',)),
    (1, 'e111-e-', ('ee11-ee-', 'ee11-ee-',)),
]
KR(gamma, R1op, R2op, 4)
printKR1(gamma)

print "4x 5loop 1"

gamma = 'e123-e45-e45-e45-5--'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 5)
printKR1(gamma)

print "4x 5loop 2"
gamma = 'e123-e23-45-45-e5-e-'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 5)
printKR1(gamma)

print "4x 5loop 3"
gamma = 'e123-e24-35-45-e5-e-'
R1op = [
]
R2op = [
]
KR(gamma, R1op, R2op, 5)
printKR1(gamma)


#G['ee12-e22-e-_']=K(f('ee12-e22-e-')+f('ee11-ee-')*KR1['ee11-ee-'])
#G['ee12-e22-e-_k']=K(4*G['ee12-e22-e-']-G['ee12-e22-e-_'])
#KR1['ee12-e22-e-_k']=K(G['ee12-e22-e-_k']-2*G['ee11-ee-']*KR1['ee11-ee-_1k']-2*G['ee11-ee-_1k']*KR1['ee11-ee-'])

#print "16+19"
##4x 4loop 16+19
#gamma=(
#    (1,'ee12-e23-e4-444--'),
#    (1,'ee12-e33-444-e4--'),
#    )
#R1op=[
#    (0.5,'ee12-e22-e-_k',('e111-e-',)),
#    (1,'ee11-ee-',('ee12-ee3-333--',)),
#    (1,'ee12-ee3-333--',('ee11-ee-',)),
#    (-1,'ee11-ee-_1k',('ee11-ee-','e111-e-',)),
#]
#KR(gamma, R1op, 4)
#printKR1(gamma)


G['ee12-e23-33-e-'] = K(KR1['ee12-e23-33-e-']+G['ee11-ee-']*KR1['ee12-e22-e-'] + G['ee12-e22-e-']*KR1['ee11-ee-'])
G['ee12-e23-33-e-_'] = K(f('ee12-e23-33-e-') + G['ee11-ee-_'] * KR1['ee12-e22-e-'] + G['ee12-e22-e-_'] * KR1[
                                                                                                         'ee11-ee-'])  #формула обратная формуле для f
G['ee12-e23-33-e-_k'] = K(6 * G['ee12-e23-33-e-'] - G['ee12-e23-33-e-_'])
#каждая линия порождает диаграмму без точки и вклад в диаграмму с \partial_{m^2}
KR1['ee12-e23-33-e-_k'] = K(
    G['ee12-e23-33-e-_k'] - G['ee11-ee-_k'] * KR1['ee12-e22-e-'] - G['ee12-e22-e-_k'] * KR1['ee11-ee-']
    - G['ee11-ee-'] * KR1['ee12-e22-e-_k'] - G['ee12-e22-e-'] * KR1['ee11-ee-_k'])

KR1['ee12-e23-33-e-_'] = K(
    G['ee12-e23-33-e-_'] - G['ee11-ee-_'] * KR1['ee12-e22-e-'] - G['ee12-e22-e-_'] * KR1['ee11-ee-']
    - G['ee11-ee-'] * KR1['ee12-e22-e-_'] - G['ee12-e22-e-'] * KR1['ee11-ee-_'])

print "\n\n\n\n======="
print (KR1['ee12-e23-33-e-_k']+KR1['ee12-e23-33-e-_']).sympy_series()
print (KR1['ee12-e23-33-e-_']).sympy_series()
print (6*KR1['ee12-e23-33-e-']).sympy_series()



print "4x 5loop 4 + 5 + 6 + 12 + 2* 16"
gamma = (
    (1, 'ee12-e23-44-555-e5--'),
    (1, 'ee12-e34-335-e-555--'),
    (1, 'ee12-333-445-5-e5-e-'),
    (1, 'ee12-e34-555-e44-5--'),
    (2, 'ee12-e23-34-e5-555--'),
)

R1op = [
    (1, 'ee12-e23-33-e-_k', ('e111-e-',)),
    (1, "((2, 'ee12-e23-e4-444--'), (2, 'ee12-e33-444-e4--'))", ('ee11-ee-',)),
    #    (2,'ee12-e23-e4-444--',('ee11-ee-',)),
    #    (2,'ee12-e33-444-e4--',('ee11-ee-',)),
    (-1, 'ee12-e22-e-_k', ('ee11-ee-', 'e111-e-')),
    (-1, 'ee11-ee-_k', ('ee12-e22-e-', 'e111-e-')),
    (2, 'ee12-ee3-333--', ('ee12-e22-e-',)),
    (2, 'ee12-e22-e-', ('ee12-ee3-333--',)),
    (1, 'ee11-ee-', ("((2, 'ee12-e23-e4-444--'), (2, 'ee12-e33-444-e4--'))",) )
    #    (2,'ee11-ee-',('ee12-e23-e4-444--',)),
    #    (2,'ee11-ee-',('ee12-e33-444-e4--',)),
]
R2op = [
    (1, 'ee12-e23-33-e-_k', ('e111-e-',)),
    (1, 'ee12-e23-33-e-_', ('e111-e-_tau',)),
    (1, "((2, 'ee12-e23-e4-444--'), (2, 'ee12-e33-444-e4--'))", ('ee11-ee-',)),
    (1, 'ee12-e22-e-_k', ('ee11-ee-', 'e111-e-')),
    (1, 'ee12-e22-e-_', ('ee11-ee-', 'e111-e-_tau')),
    (1, 'ee11-ee-_k', ('ee12-e22-e-', 'e111-e-')),
    (1, 'ee11-ee-_', ('ee12-e22-e-', 'e111-e-_tau')),
    (2, 'ee12-ee3-333--', ('ee12-e22-e-',)),
    (2, 'ee12-e22-e-', ('ee12-ee3-333--',)),
    (1, 'ee11-ee-', ("((2, 'ee12-e23-e4-444--'), (2, 'ee12-e33-444-e4--'))",) )
]
KR(gamma, R1op, R2op, 5)
printKR1(gamma)



print "\n\n\n\n\n============"
print 'ee11-ee-_'
print G['ee11-ee-_']
print K(2*G['ee11-ee-_1'])
print K(f('ee11-ee-'))
print 'ee11-ee-_k'
print G['ee11-ee-_k']
print K(2*G['ee11-ee-_1k'])
print K(2*G['ee11-ee-']-G['ee11-ee-_'])
print "\n\n\n\n\n============"


C1 = Series([[Number(0.5, 0), 1]])
C2 = Series([[Number(3, 0), 0], [Number(-1.25, 0), 1], [Number(0.125, 0), 2]])
C3 = Series([[Number(6, 0), 0], [Number(-1.5, 0), 1]])

G['ee11-ee-_k_'] = K(C1 * G['ee11-ee-_k'])
G['ee11-ee-_k_k'] = K(C2 * G['ee11-ee-'])  # неверно?
G['ee11-ee-_k_k'] = K(2*C2 * G['ee11-ee-'])
KR1['ee11-ee-_k_k'] = G['ee11-ee-_k_k']
KR1['ee11-ee-_k_'] = G['ee11-ee-_k_']
KR1['ee11-ee-__'] = K(3*G['ee11-ee-_']-G['ee11-ee-_k_'])
G['ee11-ee-__'] = K(3*G['ee11-ee-_']-G['ee11-ee-_k_'])

print 'ee11-ee-__'
print KR1['ee11-ee-__']
print K(Series([[Number(1, 0), 0], [Number(0.5, 0), 1]])*f('ee11-ee-'))
print 'ee11-ee-_k_'
print G['ee11-ee-_k_']
print K(3*G['ee11-ee-_'] - G['ee11-ee-__'])
print 'ee11-ee-_k_k'
print G['ee11-ee-_k_k']
print K(3*G['ee11-ee-_k'] - G['ee11-ee-_k_'])

print "\n\n\n\n\n============"




print "\n\n\n\n\n============"


KR1['ee12-ee3-333--_']= K( f('ee12-ee3-333--') - 0.5 * G['ee11-ee-_k']*f('e111-e-'))
KR1['ee12-ee3-333--_k'] = K(6*KR1['ee12-ee3-333--'] - KR1['ee12-ee3-333--_'])
print K(KR1['ee12-ee3-333--_k'] + KR1['ee12-ee3-333--_'])
print "   ", K( KR1['ee12-ee3-333--_'])
print "   ", K( KR1['ee12-ee3-333--_k'])
print K(6*KR1['ee12-ee3-333--'])

print


#G['ee11-22-ee-'] = K( G['ee11-ee-'] * G['ee11-ee-'])
#G['ee12-223-3-ee-'] = K(KR1['ee12-223-3-ee-']
#                        + 2 * G['ee11-ee-']*KR1['ee12-e22-e-']
#                        + G['ee11-22-ee-']*KR1['ee11-ee-'])

#R1_ms['e112-e3-333--_tau'] = K(R1_ms["((2, 'ee12-e23-e4-444--'), (2, 'ee12-e33-444-e4--'))"]
#                           + 2 * (G['ee11-ee-'] * KR1_ms['ee12-ee3-333--'] + G['ee12-ee3-333--'] * KR1_ms['ee11-ee-'])
#                           + 3 * (R1_ms['ee12-223-4-e44-e-'] + G['ee12-223-3-ee-']*KR1_ms['ee11-ee-'])
#                       )
R1_ms['e112-e3-333--_tau'] = K(Series([[Number(0, 0), 0],]))
#R1_ms['e112-e3-333--_tau'] = K(Seres([[Number(11, 0), 0],[Number(11, 0), 1],[Number(11, 0), 2],[Number(11, 0), 3],]))
KR1_ms['e112-e3-333--_tau'] = K_ms(R1_ms['e112-e3-333--_tau'])



print "4x 5loop 14 + 6*15 + 2*23"
gamma = (
    (1, 'ee12-333-444-5-5-ee-'),
    (6, 'ee12-ee3-334-5-555--'),
    (2, 'ee12-ee3-444-555-5--'),
)

R1op = [
    (2, 'ee12-ee3-333--_k', ('e111-e-',)),
    (-0.5, 'ee11-ee-_k_k', ('e111-e-', 'e111-e-',)),
    (3, 'ee11-ee-_k', ('e112-e3-333--',)),
    ]

R2op = [
    (2, 'ee12-ee3-333--_k', ('e111-e-',)),
    (2, 'ee12-ee3-333--_', ('e111-e-_tau',)),
    (0.5, 'ee11-ee-_k_k', ('e111-e-', 'e111-e-',)),
    (1*2, 'ee11-ee-_k_', ('e111-e-', 'e111-e-_tau',)),
    (1, 'ee11-ee-__', ('e111-e-_tau', 'e111-e-_tau',)),
    (3, 'ee11-ee-_k', ('e112-e3-333--',)),
    (3, 'ee11-ee-_', ('e112-e3-333--_tau',)),
]
KR(gamma, R1op, R2op, 5)
print
print K(KR1[str(gamma)]).sympy_series()
printKR1(gamma)





sys.exit()

print
#print G[str(gamma)].sympy_series()
print KR1[str(gamma)].sympy_series()

print "4x 5loop 7"
print "4x 5loop 8"
print "4x 5loop 10"
print "4x 5loop 11"

print "4x 5loop 13"

print "4x 5loop 17"
print "4x 5loop 18"
print "4x 5loop 19"
print "4x 5loop 20"
print "4x 5loop 21"
print "4x 5loop 22"

print "4x 5loop 24"

gamma = 'e112-34-e35-45-e5-e-'
R1op = [
    (1, 'e123-e24-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 25"
gamma = 'e123-e24-55-e45-e5--'
R1op = [
    (1, 'e123-e24-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 26"
gamma = 'ee12-234-35-45-e5-e-'
R1op = [
    (1, 'ee11-ee-', ('e123-e24-34-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 27"
gamma = 'e112-34-345-e5-e5-e-'
R1op = [
    (1, 'e123-e24-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 28"
gamma = 'e123-e45-e45-445--e-'
R1op = [
    (1, 'e123-e24-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 29"
gamma = 'ee12-345-345-e4-5-e-'
R1op = [
    (1, 'ee11-ee-', ('e123-e24-34-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 30"
gamma = 'e112-33-e45-45-e5-e-'
R1op = [
    (2, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (1, 'e123-e23-e3-e-', ('ee11-22-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 31"
gamma = 'ee11-23-345-45-e5-e-'
R1op = [
    (-1, 'ee11-ee-', ('ee11-ee-', 'e123-e23-e3-e-')),
    (1, 'ee11-22-ee-', ('e123-e23-e3-e-',)),
    (1, 'ee12-234-34-e4-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-234-34-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 32"
gamma = 'ee12-234-34-45-5-ee-'
R1op = [
    (1, 'ee11-22-ee-', ('e123-e23-e3-e-',)),
    (2, 'ee11-ee-', ('ee12-234-34-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 33"
gamma = 'e112-23-45-e45-e5-e-'
R1op = [
    (1, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (1, 'e123-e23-e3-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 34"
gamma = 'e123-e24-e5-e45-55--'
R1op = [
    (1, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (1, 'e123-e23-e3-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 35"
gamma = 'e112-e3-345-45-e5-e-'
R1op = [
    (1, 'ee12-e22-e-', ('e123-e23-e3-e-',)),
    (1, 'ee12-234-34-e4-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'e123-e23-e3-e-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 36"
gamma = 'ee12-e34-345-45-5-e-'
R1op = [
    (1, 'ee12-e22-e-', ('e123-e23-e3-e-',)),
    (1, 'ee11-ee-', ('ee12-234-34-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 37"
gamma = 'ee12-334-345-5-e5-e-'
R1op = [
    (1, 'ee11-ee-', ('e112-34-e34-e4-e-',)),
    (1, 'ee12-234-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 38"
gamma = 'ee12-234-35-e4-55-e-'
R1op = [
    (1, 'ee11-ee-', ('e112-34-e34-e4-e-',)),
    (1, 'ee12-234-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 39"
gamma = 'e112-34-e35-e5-e55--'
R1op = [
    (2, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (-1, 'e123-e23-e3-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 40"
gamma = 'e112-34-e34-e5-55-e-'
R1op = [
    (2, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (-1, 'e123-e23-e3-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 41"
gamma = 'e112-34-e55-e45-e5--'
R1op = [
    (2, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (-1, 'e123-e23-e3-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 42"
gamma = 'ee12-234-34-e5-55-e-'
R1op = [
    (1, 'ee11-ee-', ('e112-34-e34-e4-e-',)),
    (1, 'ee12-234-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 43"
gamma = 'ee12-233-45-45-e5-e-'
R1op = [
    (1, 'ee11-ee-', ('e112-34-e34-e4-e-',)),
    (1, 'ee12-234-34-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 44"
gamma = 'e112-34-e35-e4-55-e-'
R1op = [
    (2, 'e112-34-e34-e4-e-', ('ee11-ee-',)),
    (-1, 'e123-e23-e3-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 45"
gamma = 'e112-23-e4-e55-e55--'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (-2, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e112-e3-e44-e44--', ('ee11-ee-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 46"
gamma = 'ee11-23-e34-45-55-e-'
R1op = [
    (1, 'ee11-22-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee11-ee-', ('ee12-e23-34-44-e-',)),
    (1, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (1, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 47"
gamma = 'ee12-234-35-44-5-ee-'
R1op = [
    (1, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (1, 'ee12-223-3-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee11-ee-', ('ee12-e34-334-4-e-',)),
    (1, 'ee11-ee-', ('ee12-e23-34-44-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 48"
gamma = 'ee11-23-e45-445-5-e-'
R1op = [
    (1, 'ee11-22-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e34-334-4-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (1, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 49"
gamma = 'e112-e3-e34-55-e55--'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e33-e33--')),
    (2, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'e112-e3-e33-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 50"
gamma = 'ee12-e23-34-55-e55--'
R1op = [
    (1, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (1, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (2, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e23-44-e44--',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 51"
gamma = 'ee12-e34-355-e4-55--'
R1op = [
    (1, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (2, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e23-44-e44--',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 52"
gamma = 'e112-23-e4-e45-55-e-'
R1op = [
    (-1, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (2, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 53"
gamma = 'ee12-e34-355-45-e5--'
R1op = [
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e23-34-44-e-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 54"
gamma = 'ee12-e23-34-45-55-e-'
R1op = [
    (1, 'ee11-ee-', ('ee12-e23-34-44-e-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 55"
gamma = 'e112-e3-e45-445-5-e-'
R1op = [
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (1, 'e112-e3-e33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 56"
gamma = 'ee12-e33-345-4-55-e-'
R1op = [
    (1, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-23-e34-44-e-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 57"
gamma = 'ee12-e23-44-455-5-e-'
R1op = [
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-23-e33-e-',)),
    (1, 'ee11-ee-', ('ee12-e33-344-4-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 58"
gamma = 'ee12-e34-335-5-e55--'
R1op = [
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-344-4-e-',)),
    (1, 'ee12-e22-e-', ('ee11-23-e33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 59"
gamma = 'ee12-e33-445-45-5-e-'
R1op = [
    (1, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-23-e34-44-e-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 60"
gamma = 'e112-e3-e44-455-5-e-'
R1op = [
    (1, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-23-e33-e-',)),
    (-1, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e112-e3-e44-e44--', ('ee11-ee-',)),
    (1, 'e112-e3-e33-e-', ('ee12-e22-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-23-e33-e-')),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 61"
gamma = 'ee12-233-34-5-e55-e-'
R1op = [
    (1, 'ee12-223-4-e44-e-', ('ee11-ee-',)),
    (1, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-ee-', ('e112-e3-e34-44-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (1, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 62"
gamma = 'ee12-223-4-e45-55-e-'
R1op = [
    (1, 'ee12-223-4-e44-e-', ('ee11-ee-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-223-3-ee-', ('ee12-e22-e-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('e112-e3-e34-44-e-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 63"
gamma = 'ee12-233-45-e4-55-e-'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('e112-e3-e34-44-e-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-233-44-e4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 64"
gamma = 'ee12-e34-335-4-55-e-'
R1op = [
    (1, 'ee12-e22-e-', ('e112-e3-e33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-233-44-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 65"
gamma = 'ee12-334-355-4-e5-e-'
R1op = [
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('e112-e3-e34-44-e-',)),
    (1, 'ee12-233-44-e4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 66  !!!!!!!!!!!---------------------!!!!!!!!!!!!!!!!!!!!---------------------!!!!!!!!!!!!1"

print "4x 5loop 67"
gamma = 'ee12-e34-334-5-55-e-'
R1op = [
    (1, 'ee11-ee-', ('ee12-334-344-e-e-',)),
    (1, 'ee12-e22-e-', ('e112-e3-e33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 68"
gamma = 'e112-e3-445-455-e-e-'
R1op = [
    (2, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'e112-e3-e33-e-')),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-1, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-334-344-e-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('e112-e3-e33-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 69"
gamma = 'ee12-334-455-e5-e5--'
R1op = [
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('e112-e3-e34-44-e-',)),
    (1, 'ee12-334-344-e-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 70"
gamma = 'ee12-334-345-e-55-e-'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('e112-e3-e34-44-e-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-334-344-e-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 71"
gamma = 'ee12-334-355-e-e55--'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('e112-e3-e44-e44--',)),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-334-344-e-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 72"
gamma = 'ee11-23-445-455-e-e-'
R1op = [
    (2, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'e112-e3-e33-e-')),
    (1, 'ee11-ee-', ('ee12-334-344-e-e-',)),
    (1, 'ee11-22-ee-', ('e112-e3-e33-e-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-334-344-e-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 73"
gamma = 'ee12-334-344-5-5-ee-'
R1op = [
    (2, 'ee11-ee-', ('ee12-334-344-e-e-',)),
    (2, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-ee-', ('e112-e3-e33-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 74"
gamma = 'ee12-e23-45-445-5-e-'
R1op = [
    (1, 'ee11-ee-', ('ee12-e34-334-4-e-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 75"
gamma = 'ee12-e34-345-e5-55--'
R1op = [
    (1, 'ee11-ee-', ('ee12-e34-334-4-e-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (1, 'ee12-e34-334-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 76"
gamma = 'e112-e3-e34-45-55-e-'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e23-34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (1, 'e112-e3-e33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 77"
gamma = 'e112-23-e4-e45-55-e-'
R1op = [
    (-1, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (2, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 78"
gamma = 'ee11-23-e44-e55-55--'
R1op = [
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (-3, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee11-23-e33-e-', ('ee11-22-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-22-33-ee-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-33-ee-')),
    (3, 'ee11-23-e44-e44--', ('ee11-ee-',)),
    (1, 'ee12-e33-e44-44--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee12-e33-e44-44--',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 79"
gamma = 'ee12-334-455-55-ee--'
R1op = [
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (3, 'ee12-334-334--ee-', ('ee11-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-22-33-ee-',)),
    (2, 'ee11-ee-', ('ee12-e33-e44-44--',)),
    (2, 'ee12-223-3-ee-', ('ee11-22-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 80"
gamma = 'ee11-22-34-e55-e55--'
R1op = [
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e33-e33--')),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee11-ee-', ('ee11-23-e44-e44--',)),
    (2, 'ee11-22-34-e44-e-', ('ee11-ee-',)),
    (1, 'ee11-22-ee-', ('ee12-e33-e33--',)),
    (-4, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e33-e33--', ('ee11-22-ee-',)),
    (1, 'ee11-22-33-ee-', ('ee11-22-ee-',)),
    (-1, 'ee11-ee-', ('ee11-22-ee-', 'ee11-22-ee-')),
    (2, 'ee11-23-e44-e44--', ('ee11-ee-',)),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 81"
gamma = 'ee11-23-445-445--ee-'
R1op = [
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e33-e33--')),
    (1, 'ee12-334-334--ee-', ('ee11-ee-',)), #
    (1, 'ee11-ee-', ('ee11-23-e44-e44--',)),
    (2, 'ee11-22-ee-', ('ee12-e33-e33--',)), #
    (1, 'ee11-22-33-ee-', ('ee11-22-ee-',)),
    (-2, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee12-334-334--ee-',)), #
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
    (2, 'ee11-23-334-4-ee-', ('ee11-ee-',)), #
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 82"
gamma = 'ee12-e23-44-e55-55--'
R1op = [
    (3, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-22-33-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-e44-44--',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 83"
gamma = 'ee11-22-34-e45-55-e-'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee11-22-33-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee12-e23-33-e-',)),
    (1, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (2, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-22-ee-', 'ee12-e22-e-')),
    (1, 'ee11-22-34-e44-e-', ('ee11-ee-',)),
    (-2, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-23-e34-44-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 84"
gamma = 'ee11-23-344-45-5-ee-'
R1op = [
    (1, 'ee11-ee-', ('ee12-233-34-4-ee-',)),
    (1, 'ee11-22-33-ee-', ('ee12-e22-e-',)),
    (1, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (2, 'ee11-22-ee-', ('ee12-e23-33-e-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-ee-', ('ee11-23-e34-44-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-23-334-4-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 85"
gamma = 'ee12-e33-e44-55-55--'
R1op = [
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (-3, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (3, 'ee12-e33-e33--', ('ee11-22-ee-',)),
    (1, 'ee11-ee-', ('ee11-22-33-44-ee-',)),
    (4, 'ee12-e33-e44-44--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-22-33-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 86"
gamma = 'ee12-e23-44-e55-55--'
R1op = [
    (3, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee11-22-33-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-e44-44--',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 87"
gamma = 'ee11-23-344-55-e5-e-'
R1op = [
    (2, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'e112-e3-e33-e-')),
    (1, 'ee11-22-ee-', ('e112-e3-e33-e-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee12-233-44-e4-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-233-44-e4-e-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 88"
gamma = 'ee12-233-44-45-5-ee-'
R1op = [
    (2, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-ee-', ('e112-e3-e33-e-',)),
    (2, 'ee11-ee-', ('ee12-233-44-e4-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 89"
gamma = 'ee12-e33-344-5-55-e-'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (2, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee11-23-e44-e44--',)),
    (1, 'ee12-e33-e33--', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 90"
gamma = 'ee11-23-e44-455-5-e-'
R1op = [
    (1, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e33-344-4-e-',)),
    (1, 'ee11-22-ee-', ('ee11-23-e33-e-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-23-e44-e44--', ('ee11-ee-',)),
    (1, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-23-e33-e-')),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 91"
gamma = 'ee12-334-335--e55-e-'
R1op = [
    (2, 'ee12-223-4-e44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e33-e33--')),
    (1, 'ee11-ee-', ('e112-e3-e44-e44--',)),
    (1, 'ee12-334-334--ee-', ('ee11-ee-',)),
    (1, 'ee11-23-e33-e-', ('ee11-22-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (-2, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 92"
gamma = 'ee12-223-4-e55-e55--'
R1op = [
    (2, 'ee12-223-4-e44-e-', ('ee11-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-ee-', ('e112-e3-e44-e44--',)),
    (1, 'ee11-23-e44-e44--', ('ee11-ee-',)),
    (-2, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-223-3-ee-', ('ee11-22-ee-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee11-22-ee-')),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 93"
gamma = 'ee12-334-355-5-ee5--'
R1op = [
    (1, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (1, 'ee12-223-3-ee-', ('ee12-e22-e-',)),
    (1, 'ee12-334-334--ee-', ('ee11-ee-',)),
    (2, 'ee11-ee-', ('ee12-e33-344-4-e-',)),
    (1, 'ee11-22-ee-', ('ee11-23-e33-e-',)),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 94"
gamma = 'ee11-23-e34-55-e55--'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e33-e33--')),
    (2, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-e23-44-e44--',)),
    (1, 'ee11-23-e33-e-', ('ee11-22-ee-',)),
    (1, 'ee11-22-ee-', ('ee12-e33-e33--',)),
    (-2, 'ee12-e23-33-e-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 95"
gamma = 'ee12-233-45-44-5-ee-'
R1op = [
    (2, 'ee12-233-34-4-ee-', ('ee11-ee-',)),
    (1, 'ee11-22-ee-', ('ee12-e33-e33--',)),
    (2, 'ee11-ee-', ('ee12-e23-44-e44--',)),
    (1, 'ee12-223-3-ee-', ('ee11-22-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 96"
gamma = 'e112-33-e44-e5-55-e-'
R1op = [
    (-4, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e33-e33--', ('ee11-22-ee-',)),
    (-1, 'ee11-ee-', ('ee11-22-ee-', 'ee11-22-ee-')),
    (-4, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (4, 'e112-e3-e44-e44--', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 97"
#gamma='ee12-e23-e4-455-55--'
#R1op=[
#    (1, 'ee11-ee-', ('ee12-ee3-344-44--',)),
#    (1, 'ee12-e23-e3--', ('e112-22-e-',)),
#    (2, 'ee12-e23-e4-444--', ('ee11-ee-',)),
#]
#KR(gamma, R1op, 5)
#printKR1(gamma)



print "4x 5loop 98"
print "4x 5loop 99"
print "4x 5loop 100"
print "4x 5loop 101"
gamma = 'ee12-e34-355-44-5-e-'
R1op = [
    (1, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (1, 'ee12-e34-e34-44--', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee12-223-4-e44-e-',)),
    (1, 'ee12-e22-e-', ('e112-e3-e33-e-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 102"
gamma = 'ee12-334-455-e4-5-e-'
R1op = [
    (1, 'ee11-ee-', ('e112-e2-34-e44-e-',)),
    (2, 'ee12-e33-344-4-e-', ('ee11-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 103"
gamma = 'e112-e3-334-5-e55-e-'
R1op = [
    (2, 'ee12-223-4-e44-e-', ('ee11-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-2, 'ee11-ee-', ('ee11-ee-', 'e112-e3-e33-e-')),
    (1, 'e112-e2-34-e44-e-', ('ee11-ee-',)),
    (-2, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee12-e22-e-', ('e112-e3-e33-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 104"
gamma = 'e112-23-e4-e55-e55--'
R1op = [
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (1, 'ee12-e23-33-e-', ('ee11-22-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'e112-e3-e34-44-e-', ('ee11-ee-',)),
    (-2, 'e112-e3-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e112-e3-e44-e44--', ('ee11-ee-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 105"
gamma = 'ee11-23-334-5-e55-e-'
R1op = [
    (1, 'ee12-223-4-e44-e-', ('ee11-ee-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-23-e33-e-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'e112-e3-e33-e-')),
    (1, 'ee12-e22-e-', ('ee11-23-e33-e-',)),
    (1, 'ee11-22-ee-', ('e112-e3-e33-e-',)),
    (1, 'ee11-22-34-e44-e-', ('ee11-ee-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee12-223-4-e44-e-',)),
    (1, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (-1, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-23-334-4-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 106"
gamma = 'ee12-223-4-445-5-ee-'
R1op = [
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (2, 'ee12-223-3-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('e112-e3-e33-e-',)),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (2, 'ee11-ee-', ('ee12-223-4-e44-e-',)),
    (-1, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee11-23-334-4-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 107"
gamma = 'ee12-e34-e34-55-55--'
R1op = [
    (1, 'ee12-e33-e33--', ('ee11-22-ee-',)),
    (2, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (2, 'ee12-e34-e34-44--', ('ee11-ee-',)),
    (1, 'ee11-ee-', ('ee12-334-334--ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 108"
gamma = 'ee11-23-e45-e45-55--'
R1op = [
    (1, 'ee12-e34-e34-44--', ('ee11-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee12-e34-e34-44--',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-223-3-ee-')),
    (1, 'ee11-22-ee-', ('ee12-223-3-ee-',)),
    (1, 'ee11-23-e44-e44--', ('ee11-ee-',)),
    (2, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 109"
gamma = 'ee12-345-345-ee-55--'
R1op = [
    (1, 'ee12-334-334--ee-', ('ee11-ee-',)),
    (2, 'ee11-ee-', ('ee12-e34-e34-44--',)),
    (2, 'ee12-223-3-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee12-223-3-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 110"
gamma = 'e112-e2-34-e55-e55--'
R1op = [
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e33-e33--')),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-23-e33-e-', ('ee11-22-ee-',)),
    (2, 'e112-e2-34-e44-e-', ('ee11-ee-',)),
    (-2, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e22-e-', ('ee12-e33-e33--',)),
    (1, 'ee11-23-e44-e44--', ('ee11-ee-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee11-22-ee-')),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 111"
gamma = 'ee12-e34-e35-45-55--'
R1op = [
    (1, 'ee11-ee-', ('ee12-233-34-4-ee-',)),
    (1, 'ee12-e33-e33--', ('ee12-e22-e-',)),
    (1, 'ee12-e34-e34-44--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 112"
gamma = 'e112-e3-e45-e45-55--'
R1op = [
    (1, 'ee12-e34-e34-44--', ('ee11-ee-',)),
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e22-e-', ('ee12-223-3-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-223-3-ee-')),
    (1, 'e112-e3-e44-e44--', ('ee11-ee-',)),
    (2, 'e112-e3-e33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 113"
gamma = 'ee12-e23-45-e45-55--'
R1op = [
    (1, 'ee12-e23-44-e44--', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-223-3-ee-',)),
    (1, 'ee11-ee-', ('ee12-e34-e34-44--',)),
    (2, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 114"
gamma = 'e112-e2-34-e45-55-e-'
R1op = [
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-23-e34-44-e-', ('ee11-ee-',)),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (1, 'e112-e2-34-e44-e-', ('ee11-ee-',)),
    (1, 'ee12-e22-e-', ('ee12-e23-33-e-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-e23-33-e-')),
    (1, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (1, 'ee12-e23-33-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 115"

print "4x 5loop 116"
#gamma='ee12-ee3-445-455-5--'
#R1op=[
#    (-1, 'ee12-ee3-333--', ('ee11-ee-', 'ee11-ee-')),
#    (1, 'ee12-ee2--', ('e112-23-33-e-',)),
#    (2, 'ee12-ee3-344-44--', ('ee11-ee-',)),
#    (2, 'ee12-ee3-333--', ('ee12-e22-e-',)),
#]
#KR(gamma, R1op, 5)
#printKR1(gamma)

print "4x 5loop 117"
gamma = 'ee11-22-33-44-55-ee-'
R1op = [
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (3, 'ee11-22-ee-', ('ee11-22-33-ee-',)),
    (-2, 'ee11-ee-', ('ee11-ee-', 'ee11-22-33-ee-')),
    (4, 'ee11-22-33-ee-', ('ee11-22-ee-',)),
    (-1, 'ee11-ee-', ('ee11-22-ee-', 'ee11-22-ee-')),
    (2, 'ee11-ee-', ('ee11-22-33-44-ee-',)),
    (5, 'ee11-22-33-44-ee-', ('ee11-ee-',)),
    (-6, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (-6, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 118"
gamma = 'ee12-e33-e44-55-55--'
R1op = [
    (-2, 'ee12-e22-e-', ('ee11-ee-', 'ee11-22-ee-')),
    (-3, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (3, 'ee12-e33-e33--', ('ee11-22-ee-',)),
    (1, 'ee11-ee-', ('ee11-22-33-44-ee-',)),
    (4, 'ee12-e33-e44-44--', ('ee11-ee-',)),
    (2, 'ee12-e22-e-', ('ee11-22-33-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 119"
gamma = 'ee11-22-33-45-e55-e-'
R1op = [
    (1, 'ee11-22-33-ee-', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee11-22-ee-', 'ee12-e22-e-')),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-23-e33-e-')),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee11-22-33-ee-')),
    (2, 'ee11-23-e33-e-', ('ee11-22-ee-',)),
    (1, 'ee11-22-ee-', ('ee11-23-e33-e-',)),
    (3, 'ee11-22-34-e44-e-', ('ee11-ee-',)),
    (-1, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-22-34-e44-e-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-33-44-ee-', ('ee11-ee-',)),
    (-3, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-e22-e-', ('ee11-22-33-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 120"
gamma = 'ee11-22-34-445-5-ee-'
R1op = [
    (2, 'ee11-22-33-ee-', ('ee12-e22-e-',)),
    (-1, 'ee11-ee-', ('ee11-22-ee-', 'ee12-e22-e-')),
    (1, 'ee11-22-ee-', ('ee11-23-e33-e-',)),
    (-3, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-ee-', ('ee11-22-34-e44-e-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-223-3-ee-')),
    (1, 'ee11-22-ee-', ('ee12-223-3-ee-',)),
    (1, 'ee12-223-3-ee-', ('ee11-22-ee-',)),
    (1, 'ee11-22-33-44-ee-', ('ee11-ee-',)),
    (-2, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-ee-', ('ee11-23-334-4-ee-',)),
    (-1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-22-ee-')),
    (2, 'ee11-23-334-4-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 121"
gamma = 'ee11-23-334-4-55-ee-'
R1op = [
    (2, 'ee11-22-33-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-2, 'ee11-ee-', ('ee11-ee-', 'ee11-23-e33-e-')),
    (2, 'ee11-22-ee-', ('ee11-23-e33-e-',)),
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-223-3-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-22-ee-', ('ee12-223-3-ee-',)),
    (1, 'ee11-22-33-44-ee-', ('ee11-ee-',)),
    (-2, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee11-ee-', ('ee11-23-334-4-ee-',)),
    (2, 'ee11-23-334-4-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 122"
gamma = 'e112-e2-33-45-e55-e-'
R1op = [
    (-2, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee11-22-ee-', ('ee11-ee-', 'ee11-ee-', 'ee11-ee-')),
    (-2, 'ee11-ee-', ('ee11-ee-', 'ee11-23-e33-e-')),
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (2, 'ee12-e22-e-', ('ee11-23-e33-e-',)),
    (2, 'ee11-22-34-e44-e-', ('ee11-ee-',)),
    (1, 'e112-e2-34-e44-e-', ('ee11-ee-',)),
    (-2, 'ee11-23-e33-e-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (-1, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 123"
gamma = 'ee12-e33-e45-45-55--'
R1op = [
    (1, 'ee12-e34-e34-44--', ('ee11-ee-',)),
    (-1, 'ee12-e22-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (-1, 'ee12-e33-e33--', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee12-e22-e-', ('ee11-23-e33-e-',)),
    (1, 'ee12-e22-e-', ('ee12-223-3-ee-',)),
    (1, 'ee12-e33-e44-44--', ('ee11-ee-',)),
    (2, 'ee12-e33-e33--', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('ee11-23-334-4-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "4x 5loop 124"
gamma = 'ee12-223-3-45-e55-e-'
R1op = [
    (-1, 'ee11-ee-', ('ee12-e22-e-', 'ee12-e22-e-')),
    (1, 'ee12-223-3-ee-', ('ee12-e22-e-',)),
    (1, 'ee11-ee-', ('e112-e2-34-e44-e-',)),
    (1, 'ee11-22-34-e44-e-', ('ee11-ee-',)),
    (-3, 'ee11-22-ee-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'ee12-e22-e-', ('ee12-223-3-ee-',)),
    (-1, 'ee11-ee-', ('ee11-ee-', 'ee12-223-3-ee-')),
    (2, 'ee11-23-e33-e-', ('ee12-e22-e-',)),
    (-1, 'ee11-22-33-ee-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'ee11-23-334-4-ee-', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 1"

gamma = 'e112-33-e44-44--'
R1op = [
    (4, 'e112-33-e33--', ('ee11-ee-',)),
    (3, 'e112-22-e-', ('ee11-22-ee-',)),
    (2, 'e111-e-', ('ee11-22-33-ee-',)),
    (-3, 'e112-22-e-', ('ee11-ee-', 'ee11-ee-',)),
    (-2, 'e111-e-', ('ee11-22-ee-', 'ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 2"
print "2x 5loop 3"
print "2x 5loop 4"

print "2x 5loop 5"
gamma = 'e112-34-e34-44--'
R1op = [
    (1, 'e111-e-', ('ee12-223-3-ee-',)),
    (1, 'e123-e23-33--', ('ee11-ee-',)),
    (-1, 'e111-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'e112-33-e33--', ('ee11-ee-',)),
    (-1, 'e112-22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e111-e-', ('ee11-23-e33-e-',)),
    (2, 'e112-22-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 6"
gamma = 'e112-23-44-e44--'
R1op = [
    (-1, 'e111-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'e112-22-e-', ('ee11-22-ee-',)),
    (1, 'e112-33-e33--', ('ee11-ee-',)),
    (2, 'e112-23-33-e-', ('ee11-ee-',)),
    (-2, 'e112-22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e111-e-', ('ee12-e33-e33--',)),
    (1, 'e111-e-', ('ee11-23-e33-e-',)),
    (1, 'e112-22-e-', ('ee12-e22-e-',)),
    (-1, 'e111-e-', ('ee11-ee-', 'ee11-22-ee-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 7"
gamma = 'e123-e23-44-44--'
R1op = [
    (2, 'e123-e23-33--', ('ee11-ee-',)),
    (2, 'e111-e-', ('ee12-e33-e33--',)),
    (1, 'e112-22-e-', ('ee11-22-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 8"
gamma = 'e123-e24-34-44--'
R1op = [
    (2, 'e111-e-', ('ee12-e23-33-e-',)),
    (1, 'e112-22-e-', ('ee12-e22-e-',)),
    (1, 'e123-e23-33--', ('ee11-ee-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 9"
gamma = 'e112-23-34-44-e-'
R1op = [
    (2, 'e111-e-', ('ee12-e23-33-e-',)),
    (-1, 'e112-22-e-', ('ee11-ee-', 'ee11-ee-')),
    (2, 'e112-23-33-e-', ('ee11-ee-',)),
    (2, 'e112-22-e-', ('ee12-e22-e-',)),
    (-2, 'e111-e-', ('ee11-ee-', 'ee12-e22-e-')),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 10"
gamma = 'e112-34-334-4-e-'
R1op = [
    (1, 'e111-e-', ('e112-e3-e33-e-',)),
    (1, 'e123-e23-33--', ('ee11-ee-',)),
    (-1, 'e111-e-', ('ee11-ee-', 'ee12-e22-e-')),
    (1, 'e112-23-33-e-', ('ee11-ee-',)),
    (-1, 'e112-22-e-', ('ee11-ee-', 'ee11-ee-')),
    (1, 'e111-e-', ('ee12-e23-33-e-',)),
    (1, 'e112-22-e-', ('ee12-e22-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)

print "2x 5loop 11"
gamma = 'e123-234-34-4-e-'
R1op = [
    (2, 'e111-e-', ('e123-e23-e3-e-',)),
]
KR(gamma, R1op, 5)
printKR1(gamma)