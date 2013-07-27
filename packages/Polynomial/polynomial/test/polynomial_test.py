#!/usr/bin/python
# -*- coding: utf8
import unittest
from multiindex import MultiIndex
from polynomial import Polynomial
from framework.framework import PolynomialToolsTestCase

mi1_1 = MultiIndex({1: 3, 2: 4, 4: 4, 3: 1})
c1_1 = 3
mi1_2 = MultiIndex({1: 1, 5: 2})
c1_2 = 5
mi1_3 = MultiIndex()
c1_3 = 4
p1 = Polynomial({mi1_1: c1_1, mi1_2: c1_2, mi1_3: c1_3}, (1, 2), (3, 1))

mi2_1 = MultiIndex({1: 1, 2: 4, 4: 4, 3: 1})
c2_1 = 3
mi2_2 = MultiIndex({1: 1, 2: 2, 5: 2})
c2_2 = 5
p2 = Polynomial({mi2_1: c2_1, mi2_2: c2_2}, (1, 2), (3, 1))


class PolynomialTestCase(PolynomialToolsTestCase):
    def testSub(self):
        _p1 = Polynomial({mi2_1: c2_1, mi2_2: c2_2})
        _p2 = Polynomial({mi1_1: c1_1, mi1_2: c1_2, mi2_2: c2_2})
        sub = _p1 - _p2
        self.assertEquals(c2_1, sub.monomials[mi2_1])
        self.assertEquals(-c1_1, sub.monomials[mi1_1])
        self.assertIsNone(sub.monomials.get(mi2_2, None))

    def testAdd(self):
        _p1 = Polynomial({mi2_1: c2_1, mi2_2: -13})
        _p2 = Polynomial({mi1_1: c1_1, mi1_2: c1_2, mi2_2: 23})
        add = _p1 + _p2
        self.assertEquals(c2_1, add.monomials[mi2_1])
        self.assertEquals(c1_1, add.monomials[mi1_1])
        self.assertEquals(10, add.monomials[mi2_2])

    def testFactorize(self):
        f = p1.factorize()
        self.assertEquals(f[0], p1)
        self.assertEquals(len(f), 1)
        f = p2.factorize()
        self.assertEquals(f[0].monomials[MultiIndex({1: 1})], 1)
        self.assertEquals(f[1].monomials[MultiIndex({2: 1})], 1)
        self.assertEquals(len(f), 3)

    def testChangeVarToPolynomial(self):
        mi1 = MultiIndex({1: 1, 2: 1})
        mi2 = MultiIndex({2: 1, 3: 1})
        simplePolynomial = Polynomial({mi1: 1, mi2: 1}, 1, 3)
        _p1 = p2.changeVarToPolynomial(1, simplePolynomial)
        self.assertEquals(_p1.monomials[MultiIndex({2: 3, 3: 1, 5: 2})], 15)
        self.assertEquals(_p1.monomials[MultiIndex({1: 1, 2: 3, 5: 2})], 15)

    def testPowering(self):
        simplePolynomial = Polynomial({mi1_2: c1_2, mi1_3: c1_3}, 2, 3)
        _p1 = simplePolynomial._inPowerOf(1)
        self.assertEquals(_p1.c, 3)
        self.assertEquals(_p1.monomials[MultiIndex({1: 2, 5: 4})], 25)
        _p2 = simplePolynomial._inPowerOf(2)
        self.assertEquals(_p2.monomials[MultiIndex({1: 2, 5: 4})], 2400)
        self.assertEquals(_p2.c, 9)

    def testIntegration(self):
        p = Polynomial({mi1_2: c1_2, mi1_3: c1_3}, 1, 3)
        i = p.integrate(5)
        self.assertEquals(i.monomials[MultiIndex({5: 1})], 4)
        self.assertEquals(i.monomials[MultiIndex({5: 3, 1: 1})], 2.5)

    def testIntegration2(self):
        p = Polynomial({mi1_2: c1_2, mi1_3: c1_3}, 1, 3)
        mi1 = MultiIndex({1: 1, 2: 1})
        mi2 = MultiIndex({2: 1, 3: 1})
        simplePolynomial = Polynomial({mi1: 1, mi2: 1}, 1, 3)
        _p = p.changeVarToPolynomial(1, simplePolynomial)
        i = _p.integrate(5)
        self.assertEquals(i.monomials[MultiIndex({5: 1})], 4)
        self.assertEquals(i.monomials[MultiIndex({5: 3, 1: 1, 2: 1})], 7.5)
        self.assertEquals(i.monomials[MultiIndex({5: 3, 2: 1, 3: 1})], 7.5)

    def assertIsNone(self, obj):
        self.assertEquals(None, obj)

if __name__ == "__main__":
    unittest.main()
