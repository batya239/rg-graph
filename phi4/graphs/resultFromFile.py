#!/usr/bin/python
# -*- coding: utf8

import sys
import os
import sympy
from utils.numbers import Number, Series, sympyseries_to_list

from dummy_model import _phi4
import utils
from graphs import Graph


def loadFromFile(fileName, nExt, struct=None):
    gRes = dict()
    gErr = dict()
    e = sympy.var('e')
    graphResults = eval(open(fileName).read())
    for graphName in graphResults:
        g = Graph(graphName)
        nLoop = g.NLoops()
        graphNExt = len(g.ExternalLines())
#        print graphName, nLoop, graphNExt

        if graphNExt != nExt:
            continue

        res_, err_ = graphResults[graphName]

        if nLoop not in gRes:
            gRes[nLoop] = 0.
            gErr[nLoop] = 0.

        if struct is not None:
            struct_ = struct[graphName]
        else:
            struct_ = 1.

        gRes[nLoop] += reduce(lambda x , y: x + y, [res_[x] * e ** x for x in range(len(res_))]) * struct_
        gErr[nLoop] += reduce(lambda x , y: x + y, [err_[x] * e ** x for x in range(len(err_))]) * struct_
    return gRes, gErr


def solve_linear(expr, var):
    a = expr.diff(var)
    b = expr.subs(var, 0)
    return -b / a


def load_structures(fname, struct=dict()):
    import copy

    res = copy.copy(struct)
    for i in range(1, 93):
        sympy.var('r%s' % i)
    for line in open(fname).readlines():
        struct_, diag = tuple(line.split(" "))
        res[diag[:-1]] = eval(struct_)
    return res


phi4 = _phi4('dummy')
if len(sys.argv) >= 3:
    g2File = sys.argv[1]
    g4File = sys.argv[2]
else:
    print "usage %s g2file g4file [struct]"
    sys.exit(1)


if len(sys.argv) == 5:
    struct = load_structures(sys.argv[3])
    struct = load_structures(sys.argv[4], struct=struct)
else:
    struct = None

resG = dict()
err = dict()
resG[2], err[2] = loadFromFile(g2File, 2, struct=struct)
resG[4], err[4] = loadFromFile(g4File, 4, struct=struct)
for G in resG.keys():
    print "G%s:\n %s \n %s\n\n"%(G, resG[G],  err[G])



sys.stdout.flush()
#sys.exit()

g, n, e = sympy.var('g n e')
A = sympy.var('A0 A1 A2 A3 A4 A5 A6 A7')
B = sympy.var('B0 B1 B2 B3 B4 B5 B6 B7')
N = phi4.target
N = 5
f2 = 0
for i in range(2, N + 1):
    f2 = f2 + B[i] * g ** i
f4 = 0
for i in range(1, N + 1):
    f4 += A[i] * g ** i
gam2 = 2 * f2 / (1 + f2)
gam4 = 2 * f4 / (1 + f2)

g2s = utils.series_f(gam2, g, N)
g4s = utils.series_f(gam4, g, N)
#print g2s
#print g4s

subs = dict()
for i in range(N + 1):
    s_a = str(A[i])
    s_b = str(B[i])
    subs_a = 0
    subs_b = 0
    for j in range(N - i + 1):
        vara = sympy.var("%s_%s" % (s_a, j))
        varb = sympy.var("%s_%s" % (s_b, j))
        subs_a += vara * e ** j
        subs_b += varb * e ** j
    subs[A[i]] = subs_a
    #    subs[A[i]]=A[i]
    subs[B[i]] = subs_b
#    subs[B[i]]=B[i]

subs_g = 0
for i in range(1, N + 1):
    varg = sympy.var('g_%s' % i)
    subs_g += varg * e ** i
subs[g] = subs_g
#subs[g]=g


zeros = []
gGs = g4s - 2 * g2s
g__ = sympy.var('g__')
gGs_ = gGs.subs(g, g__)
for var in subs:
    gGs = gGs.subs(var, subs[var])
    gGs_ = gGs_.subs(var, subs[var])
gGs_e = utils.series_lst(gGs + e, e, N)

#print gGs_
#print gGs_e
#print
subs_ = dict()
gZ = subs[g]
for i in range(1, N + 1):
    gvar = sympy.var('g_%s' % i)
    eq = gGs_e[i]
    for sub in subs_:
        eq = eq.subs(sub, subs_[sub])
    #    print eq

    res = sympy.factor(solve_linear(eq.expand(), gvar))

    subs_[gvar] = res
#print subs_

for sub in subs_:
    gZ = gZ.subs(sub, subs_[sub])


eta = g2s.subs(g, gZ)
for var in subs:
    eta = eta.subs(var, subs[var])
eta_e = utils.series_f(eta, e, N)
print
print eta_e
print

gGs__ = gGs_
gZ_ = gZ
for i in range(2, N + 1):
    bi = utils.series_lst(resG[2][i], e, N - i)
    bi_e = utils.series_lst(err[2][i], e, N - i)
    for j in range(N + 1 - i):
        eta = eta.subs(sympy.var('B%s_%s' % (i, j)), sympy.var('B%s_%s_' % (i, j)))
        gZ_ = gZ_.subs(sympy.var('B%s_%s' % (i, j)), sympy.var('B%s_%s_' % (i, j)))
        exec ('B%s_%s_=Number(%s,%s)' % (i, j, (-1) ** (i + 1) * bi[j], bi_e[j]))
#        eta=eta.subs(sympy.var('B%s_%s'%(i, j)), (-1)**(i+1)*bi[j])
#        gGs__=gGs__.subs(sympy.var('B%s_%s'%(i, j)), (-1)**(i+1)*bi[j])




for i in range(1, N + 1):
    try:
        ai = utils.series_lst(resG[4][i], e, N - i)
        ai_e = utils.series_lst(err[4][i], e, N - i)
    except:
        ai = [0.] * (N + 1 - i)
        ai_e = [0.] * (N + 1 - i)
        print "No term %s in G4" % i
    #    print ai
    for j in range(N + 1 - i):
        eta = eta.subs(sympy.var('A%s_%s' % (i, j)), sympy.var('A%s_%s_' % (i, j)))
        gZ_ = gZ_.subs(sympy.var('A%s_%s' % (i, j)), sympy.var('A%s_%s_' % (i, j)))
        exec ('A%s_%s_=Number(%s,%s)' % (i, j, (-1) ** (i) * ai[j], ai_e[j]))
#        eta=eta.subs(sympy.var('A%s_%s'%(i, j)), (-1)**(i)*ai[j])
#        gGs__=gGs__.subs(sympy.var('A%s_%s'%(i, j)), (-1)**(i)*ai[j])

#print A1_0_

print
eta = eval(str(sympyseries_to_list(utils.series_f(eta, e, N + 1), e, 0, N + 1)))
gZ_ = eval(str(sympyseries_to_list(utils.series_f(gZ_, e, N + 1), e, 0, N + 1)))
#print 'gGs__=',utils.series_f(gGs__.subs(g__, g), e, N)
print
print "eta=", eta
#eta_series=utils.series_f(eta, e, N)
eta_series_ = list()
for term in eta:
    number, pow = term
    if isinstance(number, (float, int)):
        eta_series_.append((Number(number, 0), pow))
    else:
        eta_series_.append((number, pow))
eta_series = Series(eta_series_)
#print eta_series
print
print "eta=", eta_series.sympy_series(N + 1)
print "eta_err=", eta_series.sympy_err_series(N + 1)
#print "eta n=0 ==", eta_series.subs(n, 0)

gZ_series = list()
for term in gZ_:
    number, pow = term
    if isinstance(number, (float, int)):
        gZ_series.append((Number(number, 0), pow))
    else:
        gZ_series.append((number, pow))
gZ_series = Series(gZ_series)
print
print "gZ =", gZ_series.sympy_series(N + 1)
print "gZ_err=", gZ_series.sympy_err_series(N + 1)



beta = -g * (e + g4s - 2 * g2s)
w = -g * (g4s - 2 * g2s).diff(g)

print
w_ = w.subs(g, gZ)
for var in subs:
    w_ = w_.subs(var, subs[var])
w_e_ = utils.series_f(w_, e, N)
w_e = utils.series_f(w_, e, N)
#print w_e_
#print w_e

for i in range(2, N + 1):
    bi = utils.series_lst(resG[2][i], e, N - i)
    bi_e = utils.series_lst(err[2][i], e, N - i)
    for j in range(N + 1 - i):
        w_e = w_e.subs(sympy.var('B%s_%s' % (i, j)), sympy.var('B%s_%s_' % (i, j)))
        exec ('B%s_%s_=Number(%s,%s)' % (i, j, (-1) ** (i + 1) * bi[j], bi_e[j]))

#        print 'B%s_%s_'%(i,j), eval('B%s_%s_'%(i,j))
#        eta=eta.subs(sympy.var('B%s_%s'%(i, j)), (-1)**(i+1)*bi[j])
#        gGs__=gGs__.subs(sympy.var('B%s_%s'%(i, j)), (-1)**(i+1)*bi[j])




for i in range(1, N + 1):
    try:
        ai = utils.series_lst(resG[4][i], e, N - i)
        ai_e = utils.series_lst(err[4][i], e, N - i)
    except:
        ai = [0.] * (N + 1 - i)
        ai_e = [0.] * (N + 1 - i)
        print "No term %s in G4" % i
    print ai
    for j in range(N + 1 - i):
        w_e = w_e.subs(sympy.var('A%s_%s' % (i, j)), sympy.var('A%s_%s_' % (i, j)))
        exec ('A%s_%s_=Number(%s,%s)' % (i, j, (-1) ** (i) * ai[j], ai_e[j]))
#        print 'A%s_%s_'%(i,j), eval('A%s_%s_'%(i,j))
#        eta=eta.subs(sympy.var('A%s_%s'%(i, j)), (-1)**(i)*ai[j])
#        gGs__=gGs__.subs(sympy.var('A%s_%s'%(i, j)), (-1)**(i)*ai[j])

w_e = eval(str(sympyseries_to_list(utils.series_f(w_e, e, N + 1), e, 0, N + 1)))
print
print w_e
w_series_ = list()
for term in w_e:
    number, pow = term
    if isinstance(number, (float, int)):
        w_series_.append((Number(number, 0), pow))
    else:
        w_series_.append((number, pow))
w_series = Series(w_series_)
#print eta_series
print
print "w=", w_series.sympy_series(N + 1)
print "w_err=", w_series.sympy_err_series(N + 1)


