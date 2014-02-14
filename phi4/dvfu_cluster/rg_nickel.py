#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys
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
r2Loops = int(sys.argv[2])
r4Loops = int(sys.argv[3])

r1op = eval(open(fileName).read())

Z2_new = {0: (1, 0)}
Z3_new = {0: (1, 0)}

for nickel in r1op:
    uncert = ufloat(r1op[nickel][0], r1op[nickel][1])
    graph = graphine.Graph(graph_state.GraphState.fromStr("%s::" % nickel))
    graphLoopCount = graph.getLoopsCount()
    if graphLoopCount > max(r2Loops, r4Loops):
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

Z2 = Series(r2Loops, Z2_new)
Z3 = Series(r4Loops, Z3_new)
print
print "Z2 = ", Z2
print "Z3 = ", Z3

Zg = (Z3 / Z2 ** 2)
print "Zg = ", Zg

print
g = Series(r2Loops, {1: ufloat(1, 0)})

#beta = (-2 * g / (1 + g * sympy.ln(Zg).diff(g))).series(g, 0, r4Loops + 2).removeO()
beta = (-2 * g / (1 + g * Zg.diff() / Zg))
print "\nbeta/2 = ", beta / 2

#eta = (beta * sympy.ln(Z2).diff(g)).series(g, 0, r4Loops + 1).removeO()
eta = beta * Z2.diff() / Z2
print "\neta =", eta

if __name__ == "__main__":
    #beta1 = (beta / g / 2 + 1).expand()
    beta1 = (-1 / (1 + g * Zg.diff() / Zg) + 1)
    beta1.gSeries.pop(1) ## equal to 'beta1 - g'
    #print "beta1 =",beta1

    gStar = Series(n=1, d={0: ufloat(0., 0.)}, name='τ')
    for i in range(1, r4Loops + 1):
        d = {1: ufloat(1., 0.)}
        d.update(dict(map(lambda x: (x, ufloat(0, 0.)), range(2, i + 1))))
        tau = Series(n=i, d=d, name='τ')
        #gStar = (tau - (beta1 - g).series(g, 0, i + 1).removeO().subs(g, gStar)).series(tau, 0, i + 1).removeO()
        tmp = Series(n=i, d=beta1.gSeries)
        gStar = Series(n=i + 1, d=(tau - tmp.subs(gStar)).gSeries, name='τ')#.series(tau, 0, i + 1).removeO()

    print "g*(τ) = ", gStar
    """
    #gStarS = tau + 0.716173621 * tau**2 + 0.095042867 * tau**3 + 0.086080396 * tau ** 4 - 0.204139 * tau ** 5
    gStarS = Series(n=6, d={1: 1, 2: 0.716173621, 3: 0.095042867, 4: 0.086080396, 5: -0.204139}, name='τ')
    print "\ng*_S = ", gStarS

    #etaStar = eta.subs(g, gStar).series(tau, 0, r4Loops + 1)
    etaStar = eta.subs(gStar)

    print "η* = ", etaStar

    #etaStarGS = eta.subs(g, gStarS).series(tau, 0, r4Loops + 1)
    etaStarGS = eta.subs(gStarS)
    print "\nη*_GS = ", etaStarGS
    """