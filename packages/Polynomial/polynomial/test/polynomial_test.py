#!/usr/bin/python
# -*- coding: utf8
import unittest
from multiindex import MultiIndex
from polynomial import Polynomial

mi1 = MultiIndex({1: 3, 2: 4, 4: 4, 3: 1})
c1 = 3
mi2 = MultiIndex({1: 1, 5: 2})
c2 = 5

p = Polynomial({mi1: c1, mi2: c2}, (1, 2), (3, 0))

class PolynomialTestCase(unittest.TestCase):
    def testSet1toVar(self):
        self.assertEquals(p.set1toVar(1).__repr__(), '(3 + eps*0)(3*(x_2^4)(x_3^1)(x_4^4)+5*(x_5^2))^(1 + eps*2)')
        self.assertEquals(p.set1toVar(3).__repr__(), '(3 + eps*0)(5*(x_1^1)(x_5^2)+3*(x_1^3)(x_2^4)(x_4^4))^(1 + eps*2)')

    def testSet0toVar(self):
        self.assertEquals(p.set0toVar(1).__repr__(), 'empty polynomial')
        self.assertEquals(p.set0toVar(2).__repr__(), '(3 + eps*0)(5*(x_1^1)(x_5^2))^(1 + eps*2)')
        self.assertEquals(p.set0toVar(5).__repr__(), '(3 + eps*0)(3*(x_1^3)(x_2^4)(x_3^1)(x_4^4))^(1 + eps*2)')

    def testDiff(self):
        print p.diff(1)
        print p.diff(5)
        self.assertEquals(p.diff(7).__repr__(), 'empty polynomial')


if __name__ == "__main__":
    unittest.main()

