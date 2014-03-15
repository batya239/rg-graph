#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import swiginac


class Lazy(object):
    MAX_DEPTH = 100

    def __init__(self, depth):
        self._depth = depth
        if depth > Lazy.MAX_DEPTH:
            self._get_or_eval()

    def __add__(self, other):
        return LazySum(self, other, self._depth + 1)

    __radd__ = __add__

    def __mul__(self, other):
        return LazyMul(self, LazyValue.create(other, self._depth + 1), self._depth + 1)

    __rmul__ = __mul__

    def __sub__(self, other):
        return LazySum(self, LazyNeg(LazyValue.create(other, self._depth + 1), self._depth + 1), self._depth + 1)

    def __rsub__(self, other):
        return LazySum(LazyNeg(self, self._depth + 1), LazyValue.create(other, self._depth + 1), self._depth + 1)

    def __div__(self, other):
        return LazyDiv(self, LazyValue.create(other, self._depth + 1), self._depth + 1)

    def __rdiv__(self, other):
        return LazyDiv(LazyValue.create(other, self._depth + 1), self, self._depth + 1)

    def __neg__(self):
        return LazyNeg(self, self._depth + 1)

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
    def __init__(self, obj, depth):
        self._obj = obj
        super(LazyNeg, self).__init__(depth)

    def evaluate(self):
        return -Lazy.evaluate_val(self._obj.evaluate())


class LazyValue(Lazy):
    def __init__(self, obj, depth):
        self._obj = obj
        super(LazyValue, self).__init__(depth)

    def evaluate(self):
        return Lazy.evaluate_val(self._obj)

    @staticmethod
    def create(o, current_depth=-1):
        if isinstance(o, Lazy):
            return o
        assert not isinstance(o, (int, tuple))
        return LazyValue(o, current_depth + 1)


class LazyDiv(Lazy):
    def __init__(self, a, b, depth):
        self._a = a
        self._b = b
        super(LazyDiv, self).__init__(depth)


    def evaluate(self):
        val = Lazy.evaluate_val(self._a)
        if isinstance(val, int):
            val = swiginac.numeric(val)
        return val / Lazy.evaluate_val(self._b)

class LazySum(Lazy):
    def __init__(self, a, b, depth):
        self._a = a
        self._b = b
        super(LazySum, self).__init__(depth)


    def evaluate(self):
        return Lazy.evaluate_val(self._a) + Lazy.evaluate_val(self._b)


class LazyMul(Lazy):
    def __init__(self, a, b, depth):
        self._a = a
        self._b = b
        super(LazyMul, self).__init__(depth)


    def evaluate(self):
        return Lazy.evaluate_val(self._a) * Lazy.evaluate_val(self._b)