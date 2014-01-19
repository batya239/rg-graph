#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import swiginac


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

    def _get_or_eval(self):
        if "_cached" not in self.__dict__:
            self._cached = self.evaluate()
        return self._cached

    @staticmethod
    def evaluate_val(_v):
        v = _v._get_or_eval() if isinstance(_v, Lazy) else _v
        v = v.normal() if "normal" in dir(v) else v
        return v


class LazyNeg(Lazy):
    def __init__(self, obj):
        self._obj = obj

    def evaluate(self):
        return -Lazy.evaluate_val(self._obj.evaluate())

class LazyValue(Lazy):
    def __init__(self, obj):
        self._obj = obj

    def evaluate(self):
        return Lazy.evaluate_val(self._obj)

    @staticmethod
    def create(o):
        if isinstance(o, Lazy):
            return o
        return LazyValue(o)


class LazyDiv(Lazy):
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def evaluate(self):
        val = Lazy.evaluate_val(self._a)
        if isinstance(val, int):
            val = swiginac.numeric(val)
        return val / Lazy.evaluate_val(self._b)

class LazySum(Lazy):
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def evaluate(self):
        return Lazy.evaluate_val(self._a) + Lazy.evaluate_val(self._b)


class LazyMul(Lazy):
    def __init__(self, a, b):
        self._a = a
        self._b = b

    def evaluate(self):
        return Lazy.evaluate_val(self._a) * Lazy.evaluate_val(self._b)
