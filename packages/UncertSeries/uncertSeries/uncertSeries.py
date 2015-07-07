#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

from uncertainties import ufloat, ufloat_fromstr, Variable, AffineScalarFunc
from uncertainties import __version_info__ as uncert_version
#from sympy import Add

if uncert_version < (2, 4):
    raise Warning("Version  %s of uncertanties not supported" % str(uncert_version))

class Series():
    """ This class provides a series expansion in g up to n-th order, taking into account uncertainty.

    >>> from uncertSeries import Series
    >>> s = Series() --> just a zero number with zero inaccuracy
    >>> s = Series(1,{0:1, 1:(0.1,0.03)})
    >>> s.pprint() --> '(1) * g**0 + (0.100(30)) * g**1 '
    String representation is also possible:
    >>> print s --> 1 +  0.100(30) * g**1

    Possible arguments:
        n -- number of orders of expansion (default:1 i.e. only zero power term)
        d -- dictionary with coefficients (len(d) >= n)
        name -- name of the variable with respect to which the series expansion is done (default:'g')
        analytic -- do expansion analytically, bool variable (default:False)
    """

    def __init__(self, n=1, d={}, name='g', analytic = False):
        self.n = n
        self.gSeries = d
        self.name = name
        self.analytic = analytic
        for k, v in d.items():
            try:
                if isinstance(v, (list,tuple)):
                    self.gSeries[k] = ufloat(v[0], v[1])
                elif isinstance(v,str):
                    self.gSeries[k] = ufloat_fromstr(v)
                elif isinstance(v,int):
                    self.gSeries[k] = v
                    self.analytic = True
            except:
                print "Series constructor warning: Type(v)=",type(v)
        # print "Constructor:", self.gSeries ## FIXME
        for i in range(0, n):
            if i not in d.keys():
                if self.analytic:
                    self.gSeries[i] = 0
                else:
                    self.gSeries[i] = ufloat(0, 0)

    def __lt__(self, other):
        return len(self.gSeries) < len(other.gSeries)

    def __add__(self, other):
        tmp = dict(self.gSeries)
        # print "From __add__:",self.analytic," + ",other.pprint() ## FIXME
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
        return Series(max(tmp), tmp, name=self.name, analytic=self.analytic)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-1) * other

    def __mul__(self, other):
        tmp = {}
        if isinstance(other, Series):
            stop=min(min(self.gSeries)+max(other.gSeries),max(self.gSeries)+min(other.gSeries))
            for i in self.gSeries.keys():
                for j in other.gSeries.keys():
                    if (i + j) <= stop:
                        try:
                            tmp[i + j] += self.gSeries[i] * other.gSeries[j]
                        except  KeyError:
                            tmp[i + j] = self.gSeries[i] * other.gSeries[j]
            res = Series(max(self.n, other.n), tmp, name=self.name, analytic=self.analytic)
        elif isinstance(other, (int, float, Variable, AffineScalarFunc, Add)):
            for i in self.gSeries.keys():
                tmp[i] = self.gSeries[i] * other
            res = Series(self.n, tmp, name=self.name, analytic=self.analytic)
        elif other == 0 or sum(map(lambda v: v == 0, self.gSeries.values()))==len(self.gSeries):
            return 0
        # elif isinstance(other, sympy.core.add.Add):
        #     print "\n\nself=",self
        #     print "other=",other
        #     return 0
        else:
            print "\nself =", self.gSeries, " type(self) =", type(self)
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
        res = Series(self.n, {}, self.name, analytic=self.analytic)
        if self.gSeries[0] == 1:
            c = 1.
            normedSeries = self + Series(self.n, {0:-1}, self.name, analytic=self.analytic) ## <-- это -1!
        elif self.gSeries[0] !=0:
            c = 1./self.gSeries[0]
            normedSeries = self/self.gSeries[0] + Series(self.n, {0:-1}, self.name, analytic=self.analytic) ## <-- это -1!
        else:
            raise NotImplementedError("no constant term in series: %s" % self.gSeries)
        #if self.gSeries[0] == 1:
        #    tmp = Series(self.gSeries[1:], n = self.n-1, name=self.name)
        #        for i in range(tmp.n):
        for i in range(len(self.gSeries)):
            res += (-1) ** i * normedSeries ** i
        return res * c

    def __div__(self, other):
        """ We assume that all powers of 'g' are non-negative
        """
        if isinstance(other, Series):
            return self * other.__invert__()
        elif isinstance(other, (int, float, Variable, AffineScalarFunc)):
            return self * (1. / other)
        else:
            raise NotImplementedError("type: %s; %s" % (type(other), other.__repr__()))

    def __rdiv__(self, other):
        return other * self.__invert__()

    def __pow__(self, power, modulo=None):
        if isinstance(power, int) and power > 1:
            return reduce(lambda x, y: x * y, [self] * power)
        elif isinstance(power, int) and power == 1:
            return self
        elif isinstance(power, int) and power == 0:
            if self.analytic:
                return Series(self.n, {0: 1}, self.name, analytic=self.analytic)
            else:
                return Series(self.n, {0: ufloat(1, 0)}, self.name, analytic=self.analytic)
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
        return Series(self.n, res,analytic=self.analytic)

    ## FIXME
    #def __repr__(self):
    #    return self.gSeries



    def __str__(self):
        """
        Вывод результата, обрезанного с учётом погрешности, с указанием точности последней значащей цифры
        """
        res = ''
        for g, c in sorted(self.gSeries.items()):
            if c != 0 and g == 0 and isinstance(c, int):
                res += " %d + " % (c)
            elif c != 0 and g == 0:
                res += " %s + " % (c.format('S'))
            elif c != 0 and g <= self.n and isinstance(c, (Variable, AffineScalarFunc)):
                if c.s < 1e-14:
                    res += "%s * %s**%s + " % (str(c.n), self.name, str(g))
                else:
                    res += " %s * %s**%s + " % (c.format('S'), self.name, str(g))
            elif c != 0 and g <= self.n and isinstance(c, (int, float)):
                res += "%s * %s**%s + " % (str(c), self.name, str(g))
        return res[:-2] + (" + Order(%s**%s)" % (self.name, self.n))

    __repr__ = __str__

    def coeffs(self):
        """
        Возвращает значения коэффициентов ряда (только достоверную часть)
        """
        return map(lambda x: float(x.format('S').split("(")[0]),self.gSeries.values())[:self.n+1]

    def pprint(self):
        res = ""
        for g, c in sorted(self.gSeries.items()):
            if c != 0 and g <= self.n and not self.analytic:
                res += "(%s ± %s) * %s**%s + " % (str(c.n), str(c.s), self.name, str(g))
            elif c != 0 and g <= self.n and self.analytic:
                try:
                    this_term = c.format('S')
                except AttributeError:
                    this_term = str(c)
                #res += "(%s) * %s**%s + " % (str(c), self.name, str(g))
                res += "(%s) * %s**%s + " % (this_term, self.name, str(g))
        # print res[:-2]
        return res[:-2]

    def __len__(self):
        return len(self.gSeries)

    def subs(self, point):
        res = Series(n=self.n, d={0: ufloat(0, 0)}, name=point.name, analytic=self.analytic)
        for i, c in self.gSeries.items():
            res += c * (point ** i)
        return res

    def save(self):
        """Save value to file"""
        slov = ''
        for k,v in self.gSeries.items():
            slov += "%d: '%s', "%(k,v)
        print "Series(%d, {%s}, '%s')"%(self.n,slov,self.name)


class Series2(object):
    def __init__(self, series_dict=None, name='g'):
        if series_dict is None:
            self.gSeries = dict()
            self.gSeries[0] = ufloat(0,0)
            self.name = name
            self.order = False
        else:
            self.order = False
            self.name = name
            self.gSeries = dict()
            for k, v in sorted(series_dict.items()):
                if v is None:
                    self.order = True
                    self.gSeries[k] = None
                    break
                try:
                    if isinstance(v, (list, tuple)):
                        self.gSeries[k] = ufloat(v[0], v[1])
                    elif isinstance(v, str):
                        self.gSeries[k] = ufloat_fromstr(v)
                    elif isinstance(v, (int, float)):
                        self.gSeries[k] = ufloat(v, 0)
                    elif isinstance(v, AffineScalarFunc):
                        self.gSeries[k] = v
    # analytic??
                    # elif isinstance(v, int):
                    #     self.gSeries[k] = v
                    #     self.analytic = True
                    else:
                        raise NotImplementedError
                except Exception as e:
                    print "Series constructor warning: Type(v)=", type(v), e.message
            # for i in range(min(self.gSeries.keys()), max(self.gSeries.keys())):
            #     if i not in self.gSeries:
            #         self.gSeries[i] = ufloat(0, 0)


    def __add__(self, other):
        if isinstance(other, Series2):
            AssertionError(self.name != other.name)
            s_max = max(self.gSeries.keys())
            o_max = max(other.gSeries.keys())
            s_min = min(self.gSeries.keys())
            o_min = min(other.gSeries.keys())
            order = False
            if self.order and other.order:
                stop = min(s_max, o_max)
                order = True
            elif self.order:
                stop = s_max
                order = True
            elif other.order:
                stop = o_max
                order = True
            else:
                stop = max(s_max, o_max)+1
            res = dict()
            for i in range(min(s_min, o_min), stop):
                if i in self.gSeries:
                    a = self.gSeries[i]
                else:
                    a = ufloat(0, 0)

                if i in other.gSeries:
                    b = other.gSeries[i]
                else:
                    b = ufloat(0, 0)
                res[i] = a+b
            if order:
                res[stop] = None
        return Series2(res, name=self.name)

    def __str__(self):
        res = ''
        for g, c in sorted(self.gSeries):
            if c is None:
                res += 'Order(%s**%s) + '%(self.name, g)
                break
            elif c != 0:
                res += "(%s ± %s) * %s**%s + " % (str(c.n), str(c.s), self.name, str(g))
        if len(res)==0:
            return '0'
        else:
            return res[:-3]



def Order(n, name='g'):
    return Series2({n: None}, name=name)
