#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import sys
import math
import graphine
import graph_state
from uncertainties import ufloat, Variable, AffineScalarFunc


def internalEdges(graph):
    res = list()
    for edge in graph.allEdges():
        if graph.externalVertex not in edge.nodes:
            res.append(edge)
    return res


def symmetryCoefficient(graph):
    edges = graph.allEdges()
    unique_edges = dict()
    for idx in edges:
        if idx in unique_edges:
            unique_edges[idx] += 1
        else:
            unique_edges[idx] = 1
    C = float(math.factorial(len(graph.edges(graph.externalVertex)))) / len(graph.toGraphState().sortings)

    for idxE in unique_edges:
        C = C / float(math.factorial(unique_edges[idxE]))
    return C


class Series():
    """ Класс, обеспечивающий разложение в ряд по g с точностью до n-го порядка с учётом погрешности.
    """
    def __init__(self, d={}, n = 5, name = 'g'):
        self.n = n
        self.gSeries = d
        self.name = name
        for k,v in d.items():
            #if not isinstance(v,AffineScalarFunc):
            try:
                self.gSeries[k] = ufloat(v[0],v[1])
            except:
                pass
        for i in range(0,n):
            if i not in d.keys():
                self.gSeries[i] = ufloat(0,0)
    def __lt__(self, other):
        return len(self.gSeries) < len(other.gSeries)

    def __add__(self, other):
        tmp = dict(self.gSeries)
        if isinstance(other,Series):
            stop = min(self.n,other.n)
            if stop == 0:
                stop = max(self.n,other.n)
            for g in other.gSeries.keys():
                if g <= stop:
                    try:
                        tmp[g] += other.gSeries[g]
                    except KeyError:
                        tmp[g] = other.gSeries[g]
        elif isinstance(other,(int,float)):
            tmp[0] += other
        else:
            print type(self),type(other)
            raise NotImplementedError
        return Series(tmp, len(tmp),name=self.name)
    def __radd__(self, other):
        return self+other
    def __sub__(self, other):
        return self + (-1)*other

    def __mul__(self, other):
        tmp = {}
        if isinstance(other,Series):
            stop = min(self.n,other.n)
            for i in self.gSeries.keys():
                for j in other.gSeries.keys():
                    if (i + j) <= stop:
                        try:
                            tmp[i+j] += self.gSeries[i]*other.gSeries[j]
                        except  KeyError:
                            tmp[i+j] = self.gSeries[i]*other.gSeries[j]
            res = Series(tmp,max(self.n,other.n),name=self.name)
        elif isinstance(other,(int,float,Variable,AffineScalarFunc)):
            for i in self.gSeries.keys():
                tmp[i] = self.gSeries[i]*other
            res = Series(tmp,self.n,name=self.name)
        else:
            print "\nother =",other," type(other) =",type(other)
            raise NotImplementedError
        return res
    def __rmul__(self, other):
        return self*other
    def __neg__(self):
        return self*(-1)
    def __invert__(self):
        """ Z.__invert__() = 1/Z
        1/(1+x)=Sum_i (-1)^i x^i
        """
        res = Series({},self.n,self.name)
        #if self.gSeries[0] == 1:
        #    tmp = Series(self.gSeries[1:], n = self.n-1, name=self.name)
        #        for i in range(tmp.n):
        for i in range(len(self.gSeries)):
            res += (-1)**i * (self - 1)**i
        return res
    def __div__(self, other):
        """ Пока полагаем, что все степени g неотрицательны
        """
        if isinstance(other,Series):
            return self*other.__invert__()
        elif isinstance(other,(int,float)):
            return self*(float(1)/other)
        else:
            raise NotImplementedError
    def __rdiv__(self, other):
        return other * self.__invert__()
    def __pow__(self, power, modulo=None):
        if isinstance(power,int) and power > 1:
            return reduce(lambda x,y: x*y,[self]*power)
        elif isinstance(power,int) and power == 1:
            return self
        elif isinstance(power,int) and power == 0:
            return Series({0:ufloat(1,0)},self.n,self.name)
        else:
            print "power =",power," type(power) =",type(power)
            raise NotImplementedError

    def diff(self):
        """
        Дифференцирование полинома по g
        """
        res = {}
        for i in range(len(self.gSeries)-1):
            res[i] = (i+1)*self.gSeries[i+1]
        return Series(res,self.n)
    def __repr__(self):
        return self.gSeries
    def __str__(self):
        res = ''
        for g,c in self.gSeries.items():
            if c != 0 and g <= self.n:
                res += "(%s) * %s**%s + "%(str(c),self.name,str(g))
        return res[:-2]
    def __len__(self):
        return len(self.gSeries)
    def subs(self,point):
        res = Series({0:ufloat(0,0)},n = self.n,name=point.name)
        for i,c in self.gSeries.items():
            #print "c.n * (point**i) = ",c.n * (point**i)
            res += c * (point**i)
        return res
        #return Series({0:res},n=0)
"""
Z1 = Series()
Z2 = Series({0:ufloat(-4,0.3),1:ufloat(2,.002)},1)
print "Z1 =",Z1
print "Z2 =",Z2
print "Z2.diff() =",Z2.diff()
print "Z2 =",Z2
print "1/Z2 =",1/Z2
print "Z1*Z2 =",Z1*Z2
print "Z2**2 =",Z2**2
"""

fileName = sys.argv[1]
nLoops = int(sys.argv[2])

r1op = eval(open(fileName).read())

Z2_new = {0:(1,0)}
Z3_new = {0:(1,0)}

for nickel in r1op:
    uncert = ufloat(r1op[nickel][0],r1op[nickel][1])
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
            Z3_new[graphLoopCount] += float(-(-2./ 3) ** graphLoopCount * symmetryCoefficient(graph)) * uncert
        else:
            Z3_new[graphLoopCount] = float(-(-2./ 3) ** graphLoopCount * symmetryCoefficient(graph)) * uncert
    else:
        raise ValueError("invalid ext legs count: %s, %s" % (graphLoopCount, nickel))

Z2 = Series(Z2_new,4)
Z3 = Series(Z3_new,4)
print "Z2 = ", Z2
print "Z3 = ", Z3

Zg = (Z3 / Z2 ** 2)
print "Zg = ", Zg

print
g = Series({1:ufloat(1,0)})

#beta = (-2 * g / (1 + g * sympy.ln(Zg).diff(g))).series(g, 0, nLoops + 2).removeO()
beta = (-2 * g / (1 + g * Zg.diff()/Zg))
print "beta/2 = ", beta / 2

#eta = (beta * sympy.ln(Z2).diff(g)).series(g, 0, nLoops + 1).removeO()
eta = beta * Z2.diff()/Z2

#print "eta =", eta

#import sympy
#tau = sympy.var('tau')

#beta1 = (beta / g / 2 + 1).expand()
beta1 = (-1/ (1 + g * Zg.diff()/Zg) +1)
beta1.gSeries.pop(1) ## equal to 'beta1 - g'
print "beta1 =",beta1

gStar = Series({0:ufloat(0.,0.)},n=1,name='tau')
for i in range(1, nLoops):
    d = {1:ufloat(1.,0.)}
    d.update( dict(map(lambda x: (x,ufloat(0,0.)),range(2,i+1))))
    #print "\n g* =",gStar
    #print "d =",d
    tau = Series(d,n = i, name='tau')
    #gStar = (tau - (beta1 - g).series(g, 0, i + 1).removeO().subs(g, gStar)).series(tau, 0, i + 1).removeO()
    tmp = Series((beta1).gSeries,n = i)
    #print "tau =",tau,"; tmp =",tmp
    #print "tmp.subs(gStar) =",tmp.subs(gStar)
    #print "(tau - tmp.subs(gStar)) =", tau - tmp.subs(gStar)
    gStar = Series((tau - tmp.subs(gStar)).__repr__(),n = i+1, name='tau')#.series(tau, 0, i + 1).removeO()
    #print "g* =", gStar

print "gStar = ", gStar


#gStarS = tau + 0.716173621 * tau**2 + 0.095042867 * tau**3 + 0.086080396 * tau ** 4 - 0.204139 * tau ** 5
gStarS = Series({1:1,2:0.716173621,3:0.095042867,4:0.086080396,5:- 0.204139},n=5,name='tau')
print "gStarS = ", gStarS

#etaStar = eta.subs(g, gStar).series(tau, 0, nLoops + 1)
etaStar = eta.subs(gStar)
print "etaStar = ", etaStar

#etaStarGS = eta.subs(g, gStarS).series(tau, 0, nLoops + 1)
etaStarGS = eta.subs(gStarS)
print "etaStarGS = ", etaStarGS
