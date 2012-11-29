#!/usr/bin/python
# -*- coding: utf8

class EpsPower:
    def __init__(self, a, b=0):
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

    def __eq__(self, other):
            if isinstance(other, int):
                return self.a == other and self.b == 0
            else:
                return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return not self.__eq__(other)

    def multiplyOnInt(self, other):
        if isinstance(other, int):
            return EpsPower(self.a * other, self.b * other)

    def isZero(self):
        return self.a == 0 and self.b == 0

    def isInt(self):
        return self.b == 0

    def __hash__(self):
        return hash(self.a) + 31 * hash(self.b)

    def __repr__(self):
        return '%s+eps*%s' % (self.a, self.b)

    def __mul__(self, other):
        otherEpsPower = epsPower(other)
        if otherEpsPower.isInt():
            return EpsPower(self.a * otherEpsPower.a, self.b * otherEpsPower.a)
        else:
            raise ValueError, "couldn't multiply %s on %s" % (self, other)

    __rmul__ = __mul__


def epsPower(power):
    """creates EpsPower from tuple or return argument if it's EpsPower
    """
    if isinstance(power, tuple):
        return EpsPower(power[0], power[1])
    elif isinstance(power, int):
        return EpsPower(power)
    elif isinstance(power, EpsPower):
        return power
    else: raise AssertionError, 'power should be correct type'

ONE = epsPower(1)

ZERO = epsPower(0)