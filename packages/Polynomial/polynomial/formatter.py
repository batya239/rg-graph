#!/usr/bin/python
# -*- coding: utf8

def format(obj, exportType):
    """
    export type should one of (PYTHON, CPP)
    """
    if isinstance(obj, list):
        return map(lambda pp: _format(pp, exportType), obj)
    else:
        return _format(obj, exportType)

def _format(polynomialProduct, exportType):
    """
    export type should one of (PYTHON, CPP)
    """
    if exportType == 'PYTHON':
        return PythonFormatter().format(polynomialProduct)
    elif exportType == 'CPP':
        return CppFormatter().format(polynomialProduct)
    elif exportType == 'HUMAN':
        return HumanReadableFormatter().format(polynomialProduct)
    else:
        raise ValueError, 'export type %s is unknown' % exportType

def formatRepr(polynomialProduct):
    return format(polynomialProduct, 'HUMAN')


class AbstractFormatter:
    def format(self, pp):
        return '0' if pp.isZero() else self.multiplicationSign().join(
            map(lambda p: '(%s)' % self.formatPolynomial(p), pp.polynomials))

    def multiplicationSign(self):
        pass

    def degree(self, a, b):
        """
        should return representation a ^ b
        """
        pass

    def formatPolynomial(self, p):
        if not p.c:
            return '0'
        internal = '+'.join(map(lambda v: '%s%s%s' % (v[1], self.multiplicationSign(), self.formatMultiIndex(v[0])), p.monomials.items()))
        if p.c == 1:
            if not p.degree:
                return '1'
            elif p.degree == 1:
                return '(%s)' % internal
            else:
                return self.degree(internal, self.formatEpsNumber(p.degree))
        else:
            return '(%s)%s%s' % (self.formatEpsNumber(p.c), self.multiplicationSign(), self.degree(internal, self.formatEpsNumber(p.degree)))

    def formatMultiIndex(self, mi):
        if not len(mi):
            return '1'
        else:
            return self.multiplicationSign().join(
                map(lambda v: self.degree(self.formatVar(v[0]), v[1]) if v[1] <> 1 else self.formatVar(v[0]),
                    mi.vars.items()))

    def formatVar(self, var):
        return 'x_%s' % var if isinstance(var, int) else str(var)

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
        return "pow(%s, %s)" % (a, b)

class HumanReadableFormatter(AbstractFormatter):
    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        return "(%s)^%s" % (a, b)

class PythonFormatter(AbstractFormatter):
    def multiplicationSign(self):
        return '*'

    def degree(self, a, b):
        return "(%s)**%s" % (a, b)
