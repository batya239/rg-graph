#!/usr/bin/python
# -*- coding: utf8
"""
Tools for formatting view of integrands to other languages
"""
import polynomial
import util

HUMAN = 'HUMAN'
PYTHON = 'PYTHON'
CPP = 'CPP'

import polynomial_product


def format(obj, exportType=HUMAN):
    """
    return expression as string corresponds exportType. export type should one of (PYTHON, CPP, HUMAN)
    """
    formatter = availableFormatters[exportType]
    if isinstance(obj, list):
        return map(lambda l: Lookup.asString(l, formatter), map(lambda o: _format(o, formatter), obj))
    else:
        return Lookup.asString(_format(obj, formatter), formatter)


def formatWithExtractingNewVariables(obj, variableBasement="_A", exportType=HUMAN):
    """
    if some polynomial occurrences > 1, then it will be replaced by some variable
    """
    inlineService = PolynomialInlineService(variableBasement)
    polynomialLookupBuilder = LazyGeneratedPolynomialLookup.builder(inlineService)
    formatter = availableFormatters[exportType]
    if isinstance(obj, list):
        rawResult = map(lambda o: _format(o, formatter, polynomialLookupBuilder), obj)
        formatResult = map(lambda l: Lookup.asString(l, formatter), rawResult)
    else:
        formatResult = Lookup.asString(_format(obj, formatter, polynomialLookupBuilder), formatter)
    return formatResult, inlineService.polynomial2VariableName


def formatVarIndexes(obj, exportType=HUMAN):
    """
    obj MUST have getVarsIndexes method
    """
    formatter = availableFormatters[exportType]
    return map(lambda i: formatter.formatVar(i), obj.getVarsIndexes())


class Lookup(object):
    def getLookupString(self, formatter):
        raise NotImplementedError()

    @staticmethod
    def asString(maybeLookup, formatter):
        return maybeLookup.getLookupString(formatter) if isinstance(maybeLookup, Lookup) else str(maybeLookup)

class ConstLookup(Lookup):
    def __init__(self, const):
        self._const = const

    def getLookupString(self, formatter):
        return str(self._const)


ZERO_LOOKUP = ConstLookup("0")
ONE_LOOKUP = ConstLookup("1")


class LogLookup(Lookup):
    def __init__(self, c, power, polynomialProductLookup):
        self._c = c
        self._power = power
        self._polynomialProductLookup = polynomialProductLookup

    def getLookupString(self, formatter):
        if self._c == 1:
            if self._power == 1:
                return formatter.log(self._polynomialProductLookup.getLookupString(formatter))
            else:
                return formatter.degree(formatter.log(self._polynomialProductLookup.getLookupString(formatter)),
                                        self._power)
        else:
            return '%s%s%s' % (self._c,
                               formatter.multiplicationSign(),
                               formatter.degree(formatter.log(self._polynomialProductLookup.getLookupString(formatter)),
                                                self._power))


class PolyProdLookup(Lookup):
    def __init__(self, polynomialLookups):
        self._polynomialLookups = polynomialLookups

    def getLookupString(self, formatter):
        return formatter.multiplicationSign().join(
            map(lambda pl: '(%s)' % pl.getLookupString(formatter), self._polynomialLookups))


class PolynomialLookup(Lookup):
    pass


class PolynomialLookupBuilder(object):
    def createLookup(self, polynomial):
        raise NotImplementedError()


class LazyGeneratedPolynomialLookupBuilder(PolynomialLookupBuilder):
    def __init__(self, polynomialInlineService):
        self._polynomialInlineService = polynomialInlineService

    def createLookup(self, polynomial):
        self._polynomialInlineService.addPolynomial(polynomial)
        return LazyGeneratedPolynomialLookup(self._polynomialInlineService, polynomial)


class LazyGeneratedPolynomialLookup(PolynomialLookup):
    def __init__(self, polynomialInlineService, polynomial):
        self._polynomialInlineService = polynomialInlineService
        self._polynomial = polynomial

    def getLookupString(self, formatter):
        if self._polynomialInlineService.shouldInline(self._polynomial):
            return formatter.formatPolynomial(self._polynomial)
        else:
            return self._polynomialInlineService.getVariableFor(self._polynomial)

    @staticmethod
    def builder(polynomialInlineService):
        return LazyGeneratedPolynomialLookupBuilder(polynomialInlineService)


class PolynomialInlineService(object):
    def __init__(self, newVariablePrefix="_A"):
        self._polynomialOccurrences = util.zeroDict()
        self._polynomial2VariableName = dict()
        self._newVariablePrefix = newVariablePrefix
        self._lastVarIndex = 0

    def addPolynomial(self, polynomial):
        self._polynomialOccurrences[polynomial] += 1
        if self._polynomialOccurrences[polynomial] > 1 and polynomial not in self._polynomial2VariableName:
            self._polynomial2VariableName[polynomial] = self._newVariablePrefix + str(self._lastVarIndex)
            self._lastVarIndex += 1

    def shouldInline(self, polynomial):
        return polynomial not in self._polynomial2VariableName

    def getVariableFor(self, polynomial):
        return self._polynomial2VariableName[polynomial]

    @property
    def polynomial2VariableName(self):
        return self._polynomial2VariableName


class SimplePolynomialLookup(PolynomialLookup):
    BUILDER = None

    def __init__(self, polynomial):
        self._polynomial = polynomial

    def getLookupString(self, formatter):
        return formatter.formatPolynomial(self._polynomial)

    @staticmethod
    def builder():
        if SimplePolynomialLookup.BUILDER is None:
            class SimplePolynomialLookupBuilder(PolynomialLookupBuilder):
                def createLookup(self, polynomial):
                    return SimplePolynomialLookup(polynomial)

            SimplePolynomialLookup.BUILDER = SimplePolynomialLookupBuilder()
        return SimplePolynomialLookup.BUILDER


def _format(obj, formatter, polynomialLookupBuilder=SimplePolynomialLookup.builder()):
    return formatter.format(obj, polynomialLookupBuilder)


class AbstractFormatter:
    """
    contains main logic of expression formatting
    """

    def format(self, obj, polynomialLookupBuilder=SimplePolynomialLookup.builder()):
        if isinstance(obj, polynomial_product.Logarithm):
            return self.formatPolynomialProductLogarithm(obj, polynomialLookupBuilder)
        elif isinstance(obj, polynomial_product.PolynomialProduct):
            return self.formatPolynomialProduct(obj, polynomialLookupBuilder)
        elif isinstance(obj, polynomial.Polynomial):
            return self.formatPolynomial(obj)
        else:
            return self.formatVar(obj)

    def formatVarIndex(self, varIndex):
        """
        if var is integer
        """
        pass

    def multiplicationSign(self):
        """
        return multiplication sign
        """
        pass

    def degree(self, a, b):
        """
        return representation a ^ b
        """
        pass

    def log(self, a):
        """
        return valid log representation
        """
        pass

    def formatVar(self, varIndex):
        return self.formatVarIndex(varIndex) if isinstance(varIndex, int) else str(varIndex)

    def formatPolynomialProductLogarithm(self, log, polynomialLookupBuilder):
        if log.isZero():
            return ZERO_LOOKUP
        elif log.c == 1:
            if not log.power:
                return ONE_LOOKUP
        elif not log.power:
            return ConstLookup(log.c)

        return LogLookup(log.c, log.power, self.formatPolynomialProduct(log.polynomialProduct, polynomialLookupBuilder))

    def formatPolynomialProduct(self, pp, polynomialLookupBuilder):
        return ZERO_LOOKUP if pp.isZero() else \
            PolyProdLookup(map(lambda p: polynomialLookupBuilder.createLookup(p), pp.polynomials))

    def formatPolynomial(self, p):
        if not p.c:
            return '0'
        internal = '+'.join(map(lambda v: self.formatMultiIndex(v[0]) if v[1] == 1 else '%s%s%s' % (
            v[1], self.multiplicationSign(), self.formatMultiIndex(v[0])),
                                p.monomials.items()))
        if p.c == 1:
            if not p.degree:
                return '1'
            elif p.degree == 1:
                return '(%s)' % internal
            else:
                return self.degree(internal, self.formatEpsNumber(p.degree))
        else:
            return '(%s)%s%s' % (
                self.formatEpsNumber(p.c), self.multiplicationSign(),
                self.degree(internal, self.formatEpsNumber(p.degree)))

    def formatMultiIndex(self, mi):
        if not len(mi):
            return '1'
        else:
            return self.multiplicationSign().join(
                map(lambda v: self.degree(self.formatVar(v[0]), v[1]) if v[1] <> 1 else self.formatVar(v[0]),
                    mi.vars.items()))


    def formatEpsNumber(self, epsNumber):
        if not epsNumber.a:
            if not epsNumber.b:
                return '0'
            elif epsNumber.b < 0:
                return "-eps%s%s" % (self.multiplicationSign(), abs(epsNumber.b))
            else:
                return "eps%s%s" % (self.multiplicationSign(), epsNumber.b)
        elif not epsNumber.b:
            return str(epsNumber.a)
        elif epsNumber.b == 1:
            return '%s+eps' % epsNumber.a
        elif epsNumber.b < 0:
            return '%s-eps%s%s' % (epsNumber.a, self.multiplicationSign(), abs(epsNumber.b))
        else:
            return '%s+eps%s%s' % (epsNumber.a, self.multiplicationSign(), epsNumber.b)


class CppFormatter(AbstractFormatter):
    def formatVarIndex(self, varIndex):
        return 'u%s' % varIndex

    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        if b == 1: return a
        return 'pow(%s, %s)' % (a, b)

    def log(self, a):
        return 'log(%s)' % a


class HumanReadableFormatter(AbstractFormatter):
    """
    this formatter we use for stdouting of results
    """

    def formatVarIndex(self, varIndex):
        return 'u%s' % varIndex

    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        if b == 1: return a
        return '(%s)^(%s)' % (a, b)

    def log(self, a):
        return 'ln(%s)' % a


class PythonFormatter(AbstractFormatter):
    def formatVarIndex(self, varIndex):
        return 'u%s' % varIndex

    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        if b == 1: return a
        return '(%s)**(%s)' % (a, b)

    def log(self, a):
        return 'log(%s)' % a




availableFormatters = dict()
availableFormatters[HUMAN] = HumanReadableFormatter()
availableFormatters[CPP] = CppFormatter()
availableFormatters[PYTHON] = PythonFormatter()