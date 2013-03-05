#!/usr/bin/python
# -*- coding: utf8
import itertools

__author__ = 'daddy-bear'


class VariableAwareNumber:
    def __init__(self, varName, a, b=0):
        """Represents expression in form: a + varName*b
        """
        self._a = a
        self._b = b
        self._varName = varName

    @staticmethod
    def create(varName, number):
        if isinstance(number, tuple):
            return VariableAwareNumber(varName, number[0], number[1])
        elif isinstance(number, (int, float)):
            return VariableAwareNumber(varName, number)
        elif isinstance(number, VariableAwareNumber):
            return number
        else:
            raise AssertionError('number should be correct type: %s, value:%s' % (type(number),number))

    @staticmethod
    def getPolynomialCoefficients(varAwareNumberList):
        """
        returns list of coefficients which obtained by multiplications of VariableAwareNumbers from varAwareNumberList
        """
        c, reduced, shift = _normalize(_reduceIntegers(varAwareNumberList))
        _ord = len(reduced)
        if not _ord:
            return _shiftCoefficients([], shift)
        else:
            result = []
            for i in xrange(0, _ord + 1):
                result.append(c * reduce(lambda x, y: x + y, _xCombinations(reduced, i)))
            return _shiftCoefficients(result, shift)

    @property
    def a(self):
        return self._a
    
    @property
    def b(self):
        return self._b
    
    @property
    def varName(self):
        return self._varName

    def multiplyOnInt(self, other):
        if isinstance(other, int):
            return VariableAwareNumber(self.varName, self.a * other, self.b * other)

    def isZero(self):
        return self.a == 0 and self.b == 0

    def isRealNumber(self):
        return self.b == 0

    def __add__(self, other):
        if isinstance(other, int):
            return VariableAwareNumber(self.varName, self.a + other, self.b)
        else:
            return VariableAwareNumber(self.varName, self.a + other.a, self.b + other.b)

    def __sub__(self, other):
        if isinstance(other, int):
            return VariableAwareNumber(self.varName, self.a - other, self.b)
        else:
            return VariableAwareNumber(self.varName, self.a - other.a, self.b - other.b)

    def __neg__(self):
        return VariableAwareNumber(self.varName, -self.a, -self.b)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.a == other and self.b == 0
        elif isinstance(other, tuple):
            return self.a == other[0] and self.b == other[1]
        else:
            return self.a == other.a and self.b == other.b and self.varName == other.varName

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.a) + 31 * hash(self.b)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        if self.a == 0:
            if self.b == 0:
                return "0"
            elif self.b < 0:
                return "-%s*%s" % abs(self.b), self.varName
            else:
                return "%s*%s" % self.b, self.varName
        elif self.b == 0:
            return str(self.a)
        elif self.b == 1:
            return '%s+%s' % self.a, self.varName
        elif self.b < 0:
            return '%s-%s*%s' % (self.a, self.varName, abs(self.b))
        else:
            return '%s+%s*%s' % (self.a, self.varName, self.b)

    def __mul__(self, other):
        otherEpsPower = VariableAwareNumber.create(self.varName, other)
        if otherEpsPower.isRealNumber():
            return VariableAwareNumber(self.varName, self.a * otherEpsPower.a, self.b * otherEpsPower.a)
        elif self.isRealNumber():
            return VariableAwareNumber(self.varName, self.a * otherEpsPower.a, self.a * otherEpsPower.b)
        else:
            raise ValueError("couldn't multiply %s on %s" % (self, other))

    __rmul__ = __mul__


def _reduceIntegers(varAwareNumberList):
    """reduce all varAwareNumbers which are integers
    """
    result = []
    if not len(varAwareNumberList):
        return result
    currVariableAwareNumber = varAwareNumberList[0]
    for varAwareNumber in varAwareNumberList[1:]:
        if varAwareNumber.isRealNumber():
            currVariableAwareNumber = currVariableAwareNumber * varAwareNumber
        else:
            result.append(currVariableAwareNumber)
            currVariableAwareNumber = varAwareNumber
    result.append(currVariableAwareNumber)
    return result


def _normalize(varAwareNumberList):
    """
    removes all varAwareNumbers where VariableAwareNumber.a == 0 or VariableAwareNumber.b == 0
    and write corresponds coefficient to resultCoefficient
    """
    if not len(varAwareNumberList):
        return 0, [], 0
    resultList = []
    resultShift = 0
    resultCoefficient = 1
    for _varAwareNumber in varAwareNumberList:
        if _varAwareNumber.a == 0:
            resultShift += 1
            resultCoefficient *= _varAwareNumber.b
        elif _varAwareNumber.b == 0:
            resultCoefficient *= _varAwareNumber.a
        else:
            resultList.append(VariableAwareNumber.create(_varAwareNumber.varName, (_varAwareNumber.a, _varAwareNumber.b)))
    if not len(resultList):
        return resultCoefficient, [VariableAwareNumber.create('dummy_varname', 1)], resultShift
    return resultCoefficient, (resultList if resultList[0] != 1 else resultList[1:]), resultShift


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

