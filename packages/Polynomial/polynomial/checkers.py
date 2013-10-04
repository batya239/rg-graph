#!/usr/bin/python
# -*- coding: utf8
import multiindex

__author__ = 'daddy-bear'


class _PolynomialChecker(object):
    def __init__(self, polynomials):
        self._polynomials = polynomials

    def monomial(self, condition):
        for p in self._polynomials:
            for m, c in p.monomials.items():
                if condition._check(m, c):
                    return True
        return False

    def withMonomial(self, condition):
        return self.monomial(condition)

    def __eq__(self, other):
        if other is True:
            return len(self._polynomials) == 0
        elif other is False:
            return not len(self._polynomials) == 0
        raise AssertionError()


class _PolynomialCondition(object):
    def _check(self, polynomial):
        raise NotImplementedError

    def and_(self, anotherCondition):
        return _DoubleConditionWrapper(self, anotherCondition)


class _DoubleConditionWrapper(_PolynomialCondition):
    def __init__(self, cond1, cond2):
        self._cond1 = cond1
        self._cond2 = cond2

    def _check(self, polynomial):
        return self._cond1._check(polynomial) and self._cond2._check(polynomial)


class _ConstantPolynomialCondition(_PolynomialCondition):
    def __init__(self, constant):
        self._constant = constant

    def _check(self, polynomial):
        return polynomial.c == self._constant


class _DegreePolynomialCondition(_PolynomialCondition):
    def __init__(self, degree):
        self._degree = degree

    def _check(self, polynomial):
        return polynomial.degree == self._degree


class _AnyPolynomialCondition(_PolynomialCondition):
    def _check(self, polynomial):
        return True


_ANY_POLYNOMIAL_CONDITION = _AnyPolynomialCondition()


def degreeIs(degree):
    """
    """
    return _DegreePolynomialCondition(degree)


def coefficientIs(c):
    """
    """
    return _ConstantPolynomialCondition(c)


def anyPolynomial():
    """
    """
    return _ANY_POLYNOMIAL_CONDITION


class _MonomialCondition(object):
    def _check(self, multiIndex, constant):
        raise NotImplementedError


class _ExactMonomialCondition(_MonomialCondition):
    def __init__(self, multiIndexMap, constant):
        self._multiIndex = multiindex.MultiIndex(multiIndexMap)
        self._constant = constant

    def _check(self, multiIndex, constant):
        return self._constant == constant and self._multiIndex == multiIndex


def exactMonomial(multiIndexMap, constant):
    """
    """
    return _ExactMonomialCondition(multiIndexMap, constant)




