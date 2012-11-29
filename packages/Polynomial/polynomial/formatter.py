#!/usr/bin/python
# -*- coding: utf8

HUMAN = 'HUMAN'
PYTHON = 'PYTHON'
CPP = 'CPP'


def format(obj, exportType):
    """
    export type should one of (PYTHON, CPP)
    """
    if isinstance(obj, list):
        return map(lambda o: _format(o, exportType), obj)
    else:
        return _format(obj, exportType)


def formatRepr(polynomialProduct):
    return format(polynomialProduct, HUMAN)


def _format(obj, exportType):
    """
    export type should one of (PYTHON, CPP, HUMAN)
    """
    if exportType == PYTHON:
        formatter = PythonFormatter()
    elif exportType == CPP:
        formatter = CppFormatter()
    elif exportType == HUMAN:
        formatter = HumanReadableFormatter()
    else:
        raise ValueError, 'export type %s is unknown' % exportType
    return formatter.format(obj)

from polynomial_product import PolynomialProduct, Logarithm
from multiindex import formatVar

class AbstractFormatter:
    def format(self, obj):
        if isinstance(obj, Logarithm):
            return self.formatPolynomialProductLogarithm(obj)
        elif isinstance(obj, PolynomialProduct):
            return self.formatPolynomialProduct(obj)
        else:
            raise ValueError, 'Unsupported type %s' % type(obj)

    def multiplicationSign(self):
        pass

    def degree(self, a, b):
        """
        should return representation a ^ b
        """
        pass

    def log(self, a):
        pass

    def formatPolynomialProductLogarithm(self, log):
        if not log.c:
            return '0'
        elif log.c == 1:
            if not log.power:
                return '1'
            elif log.power == 1:
                return self.formatPolynomialProduct(log.polynomialProduct)
            else:
                return self.degree(self.log(log.polynomialProduct), log.power)
        else:
            return '%s%s%s' % (
            log.c, self.multiplicationSign(), self.degree(self.log(log.polynomialProduct), log.power))

    def formatPolynomialProduct(self, pp):
        return '0' if pp.isZero() else self.multiplicationSign().join(
            map(lambda p: '(%s)' % self.formatPolynomial(p), pp.polynomials))

    def formatPolynomial(self, p):
        if not p.c:
            return '0'
        internal = '+'.join(map(lambda v: self.formatMultiIndex(v[0]) if v[1] == 1 else '%s%s%s' % (v[1], self.multiplicationSign(), self.formatMultiIndex(v[0])),
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
            self.formatEpsNumber(p.c), self.multiplicationSign(), self.degree(internal, self.formatEpsNumber(p.degree)))

    def formatMultiIndex(self, mi):
        if not len(mi):
            return '1'
        else:
            return self.multiplicationSign().join(
                map(lambda v: self.degree(formatVar(v[0]), v[1]) if v[1] <> 1 else formatVar(v[0]),
                    mi.vars.items()))


    def formatEpsNumber(self, epsNumber):
        if not epsNumber.a:
            return "(eps%s%s)" % (self.multiplicationSign(), epsNumber.b)
        elif not epsNumber.b:
            return str(epsNumber.a)
        elif epsNumber.b == 1:
            return '(%s+eps)' % epsNumber.a
        else: return '(%s+eps%s%s)' % (epsNumber.a, self.multiplicationSign(), epsNumber.b)


class CppFormatter(AbstractFormatter):
    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        return 'pow(%s, %s)' % (a, b)

    def log(self, a):
        return 'log(%s)' % a


class HumanReadableFormatter(AbstractFormatter):
    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        return '(%s)^%s' % (a, b)

    def log(self, a):
        return 'ln(%s)' % a


class PythonFormatter(AbstractFormatter):
    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        return '(%s)**%s' % (a, b)

    def log(self, a):
        return 'log(%s)' % a
