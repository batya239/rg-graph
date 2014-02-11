#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

import math

from uncertainties import ufloat, Variable, AffineScalarFunc
from uncertainties import __version_info__ as uncert_version

if uncert_version < (2, 4):
    raise Warning("Version  %s of uncertanties not supported" % str(uncert_version))


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

    def __init__(self, n, d={}, name='g'):
        self.n = n
        self.gSeries = d
        self.name = name
        for k, v in d.items():
            try:
                self.gSeries[k] = ufloat(v[0], v[1])
            except:
                pass
        for i in range(0, n):
            if i not in d.keys():
                self.gSeries[i] = ufloat(0, 0)

    def __lt__(self, other):
        return len(self.gSeries) < len(other.gSeries)

    def __add__(self, other):
        tmp = dict(self.gSeries)
        if isinstance(other, Series):
            stop = min(self.n, other.n)
            if stop == 0:
                stop = max(self.n, other.n)
            for g in other.gSeries.keys():
                if g <= stop:
                    try:
                        tmp[g] += other.gSeries[g]
                    except KeyError:
                        tmp[g] = other.gSeries[g]
        elif isinstance(other, (int, float)):
            tmp[0] += other
        else:
            print type(self), type(other)
            raise NotImplementedError
        return Series(len(tmp), tmp, name=self.name)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-1) * other

    def __mul__(self, other):
        tmp = {}
        if isinstance(other, Series):
            stop = min(self.n, other.n)
            for i in self.gSeries.keys():
                for j in other.gSeries.keys():
                    if (i + j) <= stop:
                        try:
                            tmp[i + j] += self.gSeries[i] * other.gSeries[j]
                        except  KeyError:
                            tmp[i + j] = self.gSeries[i] * other.gSeries[j]
            res = Series(max(self.n, other.n), tmp, name=self.name)
        elif isinstance(other, (int, float, Variable, AffineScalarFunc)):
            for i in self.gSeries.keys():
                tmp[i] = self.gSeries[i] * other
            res = Series(self.n, tmp, name=self.name)
        else:
            print "\nother =", other, " type(other) =", type(other)
            raise NotImplementedError
        return res

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return self * (-1)

    def __invert__(self):
        """ Z.__invert__() = 1/Z
        1/(1+x)=Sum_i (-1)^i x^i
        """
        res = Series(self.n, {}, self.name)
        #if self.gSeries[0] == 1:
        #    tmp = Series(self.gSeries[1:], n = self.n-1, name=self.name)
        #        for i in range(tmp.n):
        for i in range(len(self.gSeries)):
            res += (-1) ** i * (self - 1) ** i
        return res

    def __div__(self, other):
        """ Пока полагаем, что все степени g неотрицательны
        """
        if isinstance(other, Series):
            return self * other.__invert__()
        elif isinstance(other, (int, float)):
            return self * (float(1) / other)
        else:
            raise NotImplementedError

    def __rdiv__(self, other):
        return other * self.__invert__()

    def __pow__(self, power, modulo=None):
        if isinstance(power, int) and power > 1:
            return reduce(lambda x, y: x * y, [self] * power)
        elif isinstance(power, int) and power == 1:
            return self
        elif isinstance(power, int) and power == 0:
            return Series(self.n, {0: ufloat(1, 0)}, self.name)
        else:
            print "power =", power, " type(power) =", type(power)
            raise NotImplementedError

    def diff(self):
        """
        Дифференцирование полинома по g
        """
        res = {}
        for i in range(len(self.gSeries) - 1):
            res[i] = (i + 1) * self.gSeries[i + 1]
        return Series(self.n, res)

    ## FIXME
    #def __repr__(self):
    #    return self.gSeries

    ## FIXME
    def _approx(self, other):
        for k, v in self.gSeries.items():
            if v != other.gSeries[k]:
                return False
        return True

    def __str__(self):
        """
        Вывод результата, обрезанного с учётом погрешности, с указанием точности последней значащей цифры
        """
        res = ''
        for g, c in self.gSeries.items():
            if c != 0 and g == 0:
                res += " %s + " % (c.format('S'))
            elif c != 0 and g <= self.n and isinstance(c, (Variable, AffineScalarFunc)):
                if c.s < 1e-14:
                    res += "%s * %s**%s + " % (str(c.n), self.name, str(g))
                else:
                    res += " %s * %s**%s + " % (c.format('S'), self.name, str(g))
            elif c != 0 and g <= self.n and isinstance(c, (int, float)):
                res += "%s * %s**%s + " % (str(c), self.name, str(g))
        return res[:-2]

    def pprint(self):
        res = ""
        for g, c in self.gSeries.items():
            if c != 0 and g <= self.n:
                res += "(%s ± %s) * %s**%s + " % (str(c.n), str(c.s), self.name, str(g))
        print res[:-2]

    def __len__(self):
        return len(self.gSeries)

    def subs(self, point):
        res = Series(n=self.n, d={0: ufloat(0, 0)}, name=point.name)
        for i, c in self.gSeries.items():
            res += c * (point ** i)
        return res


if __name__ == "__main__":
    Z1 = Series(1)
    Z2 = Series(2, {0: ufloat(-4, 0.3), 1: ufloat(2, .002)})
    print "Z1 =", Z1
    print "Z2 =", Z2
    print "Z2.diff() =", Z2.diff()
    print "Z2 =", Z2
    print "1/Z2 =", 1 / Z2
    print "Z1*Z2 =", Z1 * Z2
    print "Z2**2 =", Z2 ** 2