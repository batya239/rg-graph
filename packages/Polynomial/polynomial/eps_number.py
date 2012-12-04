#!/usr/bin/python
# -*- coding: utf8
import itertools

class EpsNumber:
    def __init__(self, a, b=0):
        """Represents power in form: a + eps*b
        """
        self.a = a
        self.b = b

    def __add__(self, other):
        if isinstance(other, int):
            return EpsNumber(self.a + other, self.b)
        else:
            return EpsNumber(self.a + other.a, self.b + other.b)

    def __sub__(self, other):
        if isinstance(other, int):
            return EpsNumber(self.a - other, self.b)
        else:
            return EpsNumber(self.a - other.a, self.b - other.b)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.a == other and self.b == 0
        else:
            return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self.__eq__(other)

    def multiplyOnInt(self, other):
        if isinstance(other, int):
            return EpsNumber(self.a * other, self.b * other)

    def isZero(self):
        return self.a == 0 and self.b == 0

    def isInt(self):
        return self.b == 0

    def __hash__(self):
        return hash(self.a) + 31 * hash(self.b)

    def __repr__(self):
        if self.a == 0:
            return "eps*%s" % self.b
        elif self.b == 0:
            return str(self.a)
        elif self.b == 1:
            return '%s+eps' % self.a
        else: return '%s+eps*%s' % (self.a, self.b)

    def __mul__(self, other):
        otherEpsPower = epsNumber(other)
        if otherEpsPower.isInt():
            return EpsNumber(self.a * otherEpsPower.a, self.b * otherEpsPower.a)
        else:
            raise ValueError, "couldn't multiply %s on %s" % (self, other)

    __rmul__ = __mul__


def epsNumber(number):
    """creates EpsPower from tuple or return argument if it's EpsPower
    """
    if isinstance(number, tuple):
        return EpsNumber(number[0], number[1])
    elif isinstance(number, int):
        return EpsNumber(number)
    elif isinstance(number, EpsNumber):
        return number
    else: raise AssertionError, 'power should be correct type'


def _reduceIntegers(epsNumberList):
    """reduce all epsNumbers which are integers
    """
    result = []
    if not len(epsNumberList):
        return result
    currEpsNumber = epsNumberList[0]
    for epsNumber in epsNumberList[1:]:
        if epsNumber.isInt():
            currEpsNumber = currEpsNumber * epsNumber
        else:
            result.append(currEpsNumber)
            currEpsNumber = epsNumber
    result.append(currEpsNumber)
    return result


def _normalize(epsNumberList):
    resultList = []
    resultCoefficient = 1
    for _epsNumber in epsNumberList:
        resultCoefficient *= _epsNumber.a
        resultList.append(epsNumber((1, _epsNumber.b / _epsNumber.a)))

    return resultCoefficient, resultList


def getCoefficients(epsNumberList):
    c, reduced = _normalize(_reduceIntegers(epsNumberList))
    ord = len(reduced)
    if not ord:
        return []
    elif ord == 1 and reduced[0].isInt():
        return c
    else:
        result = []
        for i in xrange(0, ord + 1):
            if i == 0:
                result.append(c)
            else:
                result.append(c * reduce(lambda x, y: x * y, xPerm(map(lambda n: n.b, reduced), i)))
        return result


def xPerm(A, n):
    for z in itertools.permutations(A, n):
        yield reduce(lambda x, y: x * y, z)
