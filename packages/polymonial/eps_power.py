#!/usr/bin/python
# -*- coding: utf8

class EpsPower:
    def __init__(self, a, b):
        """Represents power in form: a + eps*b
        """
        self.a = a
        self.b = b

    def __add__(self, other):
        if isinstance(other, int):
            return EpsPower(self.a + other, self.b)
        else:
            return EpsPower(self.a + other.a, self.b + other.b)

    def __sub__(self, other):
        if isinstance(other, int):
            return EpsPower(self.a - other, self.b)
        else:
            return EpsPower(self.a - other.a, self.b - other.b)

    def __repr__(self):
        return '%s + eps*%s' % (self.a, self.b)

    def isZero(self):
        return self.a == 0 and self.b == 0


def epsPower(power):
    """creates EpsPower from tuple or return argument if it's EpsPower
    """
    if isinstance(power, tuple):
        return EpsPower(power[0], power[1])
    elif isinstance(power, EpsPower):
        return power
    else: raise AssertionError, 'power should be correct type'