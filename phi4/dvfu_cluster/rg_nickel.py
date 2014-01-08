#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

from uncertSeries import *
import graphine
import graph_state

usage_message = "\nrg_nickel.py usage:\n\n$ python rg_nickel.py KR1_file r2 r4 \
                \nwhere\n\tKR1_file -- file that contains dictionary of KR'-operations over diagrams,\
                \n\tr2 -- number of loops for 2-tails,\n\tr4 -- number of loops for 4-tails."
if len(sys.argv) < 4:
    print usage_message
    exit()

fileName = sys.argv[1]
nLoops = int(sys.argv[2]) ## FIXME: сделать r2Loops и r4Loops


r1op = eval(open(fileName).read())

Z2_new = {0: (1, 0)}
Z3_new = {0: (1, 0)}

for nickel in r1op:
    uncert = ufloat(r1op[nickel][0], r1op[nickel][1])
    graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % nickel))
    graphLoopCount = graph.getLoopsCount()
    if graphLoopCount > nLoops:
        continue
    if len(graph.edges(graph.externalVertex)) == 2:
        #Z2 -= (-2 * g / 3) ** graphLoopCount * r1op[nickel] * symmetryCoefficient(graph)
        if graphLoopCount in Z2_new:
            Z2_new[graphLoopCount] += float(-(-2. / 3) ** graphLoopCount * symmetryCoefficient(graph)) * uncert
        else:
            Z2_new[graphLoopCount] = float(-(-2. / 3) ** graphLoopCount * symmetryCoefficient(graph)) * uncert
    elif len(graph.edges(graph.externalVertex)) == 4:
        if graphLoopCount in Z3_new:
            Z3_new[graphLoopCount] += float(-(-2. / 3) ** graphLoopCount * symmetryCoefficient(graph)) * uncert
        else:
            Z3_new[graphLoopCount] = float(-(-2. / 3) ** graphLoopCount * symmetryCoefficient(graph)) * uncert
    else:
        raise ValueError("invalid ext legs count: %s, %s" % (graphLoopCount, nickel))

Z2 = Series(Z2_new, nLoops)
Z3 = Series(Z3_new, nLoops)
print "Z2 = ", Z2
print "Z3 = ", Z3

Zg = (Z3 / Z2 ** 2)
print "Zg = ", Zg

print
g = Series({1: ufloat(1, 0)})

#beta = (-2 * g / (1 + g * sympy.ln(Zg).diff(g))).series(g, 0, nLoops + 2).removeO()
beta = (-2 * g / (1 + g * Zg.diff() / Zg))
print "\nbeta/2 = ", beta / 2

#eta = (beta * sympy.ln(Z2).diff(g)).series(g, 0, nLoops + 1).removeO()
eta = beta * Z2.diff() / Z2

print "\neta =", eta

#beta1 = (beta / g / 2 + 1).expand()
beta1 = (-1 / (1 + g * Zg.diff() / Zg) + 1)
beta1.gSeries.pop(1) ## equal to 'beta1 - g'
#print "beta1 =",beta1

gStar = Series({0: ufloat(0., 0.)}, n=1, name='τ')
for i in range(1, nLoops):
    d = {1: ufloat(1., 0.)}
    d.update(dict(map(lambda x: (x, ufloat(0, 0.)), range(2, i + 1))))
    tau = Series(d, n=i, name='τ')
    #gStar = (tau - (beta1 - g).series(g, 0, i + 1).removeO().subs(g, gStar)).series(tau, 0, i + 1).removeO()
    #FIXME : конструктор Series должен уметь принимать на вход объект Series и правильно его обрабатывать с точки зрения O(g)
    tmp = Series(beta1.gSeries, n=i)
    gStar = Series((tau - tmp.subs(gStar)).__repr__(), n=i + 1, name='τ')#.series(tau, 0, i + 1).removeO()

print "g* = ", gStar

#gStarS = tau + 0.716173621 * tau**2 + 0.095042867 * tau**3 + 0.086080396 * tau ** 4 - 0.204139 * tau ** 5
gStarS = Series({1: 1, 2: 0.716173621, 3: 0.095042867, 4: 0.086080396, 5: -0.204139}, n=6, name='τ')
print "g*_S = ", gStarS

#etaStar = eta.subs(g, gStar).series(tau, 0, nLoops + 1)
etaStar = eta.subs(gStar)

print "η* = ", etaStar

#etaStarGS = eta.subs(g, gStarS).series(tau, 0, nLoops + 1)
etaStarGS = eta.subs(gStarS)
print "η*_GS = ", etaStarGS
