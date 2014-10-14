#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import swiginac
import collections
from rggraphenv import symbolic_functions


class Lazy(object):
    def __add__(self, other):
        return LazySum(self, other)

    __radd__ = __add__

    def __mul__(self, other):
        return LazyMul(self, LazyValue.create(other))

    __rmul__ = __mul__

    def __sub__(self, other):
        return LazySum(self, LazyNeg(LazyValue.create(other)))

    def __rsub__(self, other):
        return LazySum(LazyNeg(self), LazyValue.create(other))

    def __div__(self, other):
        return LazyDiv(self, LazyValue.create(other))

    def __rdiv__(self, other):
        return LazyDiv(LazyValue.create(other), self)

    def __neg__(self):
        return LazyNeg(self)

    def __str__(self):
        return str(self.evaluate())

    def evaluate(self):
        if "_cached" not in self.__dict__:
            self._cached = self._evaluate()
            if "normal" in dir(self._cached):
                self._cached = self._cached.normal()
            self._clear_refs()
        return self._cached

    @staticmethod
    def evaluate_val(_v):
        v = _v.evaluate() if isinstance(_v, Lazy) else _v
        return v


class LazyNeg(Lazy):
    def __init__(self, obj):
        self._obj = obj

    def _evaluate(self):
        return -Lazy.evaluate_val(Lazy.evaluate_val(self._obj))

    def _clear_refs(self):
        self._obj = None


class LazyValue(Lazy):
    def __init__(self, obj):
        self._obj = obj

    def _evaluate(self):
        return Lazy.evaluate_val(self._obj)

    def _clear_refs(self):
        self._obj = None

    @staticmethod
    def create(o):
        if isinstance(o, Lazy):
            return o
        if isinstance(o, int):
            o = symbolic_functions.cln(o)
        assert not isinstance(o, (float, tuple)), ("type = %s, value = %s" % (type(o), o))
        return LazyValue(o)


class LazyDiv(Lazy):
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def _evaluate(self):
        val = Lazy.evaluate_val(self._a)
        if isinstance(val, int):
            val = swiginac.numeric(val)
        return val / Lazy.evaluate_val(self._b)

    def _clear_refs(self):
        self._a = None
        self._b = None


class LazySum(Lazy):
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def _clear_refs(self):
        self._a = None
        self._b = None

    def _evaluate(self):
        return Lazy.evaluate_val(self._a) + Lazy.evaluate_val(self._b)


class LazyMul(Lazy):
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def _clear_refs(self):
        self._a = None
        self._b = None

    def _evaluate(self):
        return Lazy.evaluate_val(self._a) * Lazy.evaluate_val(self._b)


ZERO = LazyValue.create(symbolic_functions.CLN_ZERO)


def zero_lazy_dict():
    return collections.defaultdict(default_factory=lambda: ZERO)