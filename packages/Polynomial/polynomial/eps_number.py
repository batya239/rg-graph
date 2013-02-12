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

    def __neg__(self):
        return EpsNumber(-self.a, -self.b)


    def __eq__(self, other):
        if isinstance(other, int):
            return self.a == other and self.b == 0
        elif isinstance(other, tuple):
            return self.a == other[0] and self.b == other[1]
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
            if self.b==0:
                return "0"
            elif self.b<0:
                return "-eps*%s" % abs(self.b)
            else:
                return "eps*%s" % self.b
        elif self.b == 0:
            return str(self.a)
        elif self.b == 1:
            return '%s+eps' % self.a
        elif self.b <0:
            return '%s-eps*%s' % (self.a, abs(self.b))
        else: return '%s+eps*%s' % (self.a, self.b)

    def __mul__(self, other):
        otherEpsPower = epsNumber(other)
        if otherEpsPower.isInt():
            return EpsNumber(self.a * otherEpsPower.a, self.b * otherEpsPower.a)
        elif self.isInt():
            return EpsNumber(self.a * otherEpsPower.a, self.a * otherEpsPower.b)
        else:
            raise ValueError, "couldn't multiply %s on %s" % (self, other)

    __rmul__ = __mul__


def epsNumber(number):
    """creates EpsPower from tuple or return argument if it's EpsPower. Factory function
    """
    if isinstance(number, tuple):
        return EpsNumber(number[0], number[1])
    elif isinstance(number, int):
        return EpsNumber(number)
    elif isinstance(number, EpsNumber):
        return number
    else: raise AssertionError, 'power should be correct type'

def getCoefficients(epsNumberList):
    """
    returns list of coefficients which obtained by multiplications of EpsNumbers from epsNumberList
    """
    c, reduced, shift = _normalize(_reduceIntegers(epsNumberList))
    ord = len(reduced)
    if not ord:
        return _shiftCoefficients([], shift)
    else:
        result = []
        for i in xrange(0, ord + 1):
            result.append(c * reduce(lambda x, y: x + y, _xCombinations(reduced, i)))
        return _shiftCoefficients( result, shift)

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
    """
    removes all epsNumbers where EpsNumber.a == 0 or EpsNumber.b == 0
    and write corresponds coefficient to resultCoefficient
    """
    resultList = []
    resultShift = 0
    resultCoefficient = 1
    for _epsNumber in epsNumberList:
        if _epsNumber.a == 0:
            resultShift += 1
            resultCoefficient *= _epsNumber.b
        elif _epsNumber.b == 0:
            resultCoefficient *= _epsNumber.a
        else:
            resultList.append(epsNumber((_epsNumber.a, _epsNumber.b)))

    return resultCoefficient, (resultList if resultList[0] <> 1 else resultList[1:]), resultShift

def _shiftCoefficients(coefficients, shift):
    """
    add zeros to head of coefficients list
    """
    shifter = [0 for i in xrange(0, shift)]
    return shifter + coefficients

def _xCombinations(numbersList, n):
    length = len(numbersList)
    for bIndexes in itertools.combinations(xrange(0, length), n):
        bProd = reduce(lambda x, y: x * numbersList[y].b, bIndexes, 1)
        aIndexes = set([i for i in xrange(0, length)]) - set(bIndexes)
        aProd = reduce(lambda x, y: x * numbersList[y].a, aIndexes, 1)
        yield aProd * bProd
