#!/usr/bin/python
# -*- coding: utf8
import unittest
from multiindex import MultiIndex
from polynomial import Polynomial

mi1 = MultiIndex({1: 3, 2: 4, 4: 4, 3: 1})
c1 = 3
mi2 = MultiIndex({1: 1, 5: 2})
c2 = 5
mi3 = MultiIndex()
c3 = 4
p = Polynomial({mi1: c1, mi2: c2, mi3: c3}, (1, 2), (3, 1))

class PolynomialTestCase(unittest.TestCase):
    def testSet1toVar(self):
        self.assertEquals(p.set1toVar(1).__repr__(), '(3+eps*1)(4*1+3*(x_2^4)(x_3^1)(x_4^4)+5*(x_5^2))^(1+eps*2)')
        self.assertEquals(p.set1toVar(3).__repr__(),
            '(3+eps*1)(4*1+5*(x_1^1)(x_5^2)+3*(x_1^3)(x_2^4)(x_4^4))^(1+eps*2)')

    def testSet0toVar(self):
        self.assertEquals(p.set0toVar(1).__repr__(), '(3+eps*1)(4*1)^(1+eps*2)')
        self.assertEquals(p.set0toVar(2).__repr__(), '(3+eps*1)(4*1+5*(x_1^1)(x_5^2))^(1+eps*2)')
        self.assertEquals(p.set0toVar(5).__repr__(), '(3+eps*1)(4*1+3*(x_1^3)(x_2^4)(x_3^1)(x_4^4))^(1+eps*2)')

    def testDiff(self):
        self.assertEquals(p.diff(1)[0].__repr__(), '(3+eps*1)(9*(x_1^2)(x_2^4)(x_3^1)(x_4^4)+5*(x_5^2))^(0+eps*2)')
        self.assertEquals(p.diff(1)[1].__repr__(), '(1+eps*2)^(1+eps*0)')
        self.assertEquals(p.diff(5)[0].__repr__(), '(3+eps*1)(10*(x_1^1)(x_5^1))^(0+eps*2)')
        self.assertEquals(p.diff(5)[1].__repr__(), '(1+eps*2)^(1+eps*0)')
        self.assertEquals(p.diff(7)[0].__repr__(), '(0+eps*0)^(1+eps*0)')

    def testStretch(self):
        self.assertEquals(p.stretch(5, [1]).__repr__(), '(3+eps*1)(4*1+5*(x_1^1)(x_5^3)+3*(x_1^3)(x_2^4)(x_3^1)(x_4^4)(x_5^3))^(1+eps*2)')
        self.assertEquals(p.stretch(1, [7, 5]).__repr__(), '(3+eps*1)(4*1+3*(x_1^3)(x_2^4)(x_3^1)(x_4^4)+5*(x_1^3)(x_5^2))^(1+eps*2)')
        self.assertEquals(p.stretch(1, [9, 2, 5]).__repr__(), '(3+eps*1)(4*1+3*(x_1^7)(x_2^4)(x_3^1)(x_4^4)+5*(x_1^3)(x_5^2))^(1+eps*2)')
        self.assertEquals(p.stretch(7, [6, 5]).__repr__(), '(3+eps*1)(4*1+3*(x_1^3)(x_2^4)(x_3^1)(x_4^4)+5*(x_1^1)(x_5^2)(x_7^2))^(1+eps*2)')


if __name__ == "__main__":
    unittest.main()

