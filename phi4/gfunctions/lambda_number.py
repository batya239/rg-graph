#!/usr/bin/python
# -*- coding: utf8
import graph_state


class LambdaNumber(object):
    def __init__(self, number):
        if isinstance(number, int):
            self._a = number
            self._b = 0
        elif isinstance(number, tuple):
            self._a = number[0]
            self._b = number[1]
        else:
            raise ValueError("constructor parameter unsupported")

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    def asRainbow(self):
        return graph_state.Rainbow([(self.a, self.b)])

    def __add__(self, other):
        if isinstance(other, int):
            return LambdaNumber((self.a + other, self.b))
        elif isinstance(other, tuple):
            return LambdaNumber((self.a + other[0], self.b + other[1]))
        elif isinstance(other, LambdaNumber):
            return LambdaNumber((self.a + other.a, self.b + other.b))
        else:
            raise ValueError("parameter type unsupported")

    def __str__(self):
        return "LambdaNumber((" + self.a + "," + self.b + "))"

    @staticmethod
    def fromRainbow(edge):
        return LambdaNumber(edge.colors)

    @staticmethod
    def pureLambda(value):
        return LambdaNumber((0, value))

    @staticmethod
    def pureConst(value):
        return LambdaNumber((value, 0))