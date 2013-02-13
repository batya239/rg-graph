#!/usr/bin/python
# -*- coding: utf8
from string import find
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

mi2_1 = MultiIndex({1: 1, 2: 4, 3: 1, 5: 1})
c2_1 = 4
mi2_2 = MultiIndex({1: 1, 4: 2, 5: 2})
c2_2 = 6
p2 = Polynomial({mi2_1: c2_1, mi2_2: c2_2}, (2, 3), (3, 0))

pp = p1 * p2

VARS = [1, 2, 3, 4, 5, 'eps']

class PolynomialProductTestCase(PolynomialToolsTestCase):
    def testNoneEq(self):
        self.assertFalse(p1 is None)

    def testDiff(self):
        self.doTestDiff(pp, 1, VARS)
        self.doTestDiff(pp, 2, VARS)

    def testSet1ToVar(self):
        self.doTestSet1toVar(pp, 1, VARS)
        self.doTestSet1toVar(pp.set1toVar(1), 1, VARS)

    def testSet0ToVar(self):
        self.doTestSet0toVar(pp, 2, VARS)
        self.assertTrue(pp.set0toVar(1).isZero())
        self.assertTrue(pp.set0toVar(5).isZero())

    def testStretch(self):
        self.assertTrue(find(repr(pp.stretch(1, [2, 3, 7, 8])), '(u1)^(8)*(u2)^(4)*u3*(u4)'))

    def testEpsExpansion(self):
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[0].polynomials[0].degree, 1)
        self.assertEquals(len(p1.toPolyProd().epsExpansion(3)[0].polynomials), 1)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][0][0].c, 3)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][1][0].c, 3)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][1][0].power, 1)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][2][1].c, 1)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][2][1].power, 1)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][3][0].c, 0.5)
        self.assertEquals(p1.toPolyProd().epsExpansion(3)[1][3][0].power, 3)

    def testSimplifying(self):
        npp = pp.simplify()
        self.assertEquals(len(npp.polynomials), 4)
        self.assertEquals(npp.polynomials[0].monomials[MultiIndex({1: 1})], 1)
        self.assertEquals(npp.polynomials[0].degree, (2, 3))
        self.assertEquals(npp.polynomials[0].c, 1)
        self.assertEquals(npp.polynomials[2].monomials[MultiIndex({2: 4, 3: 1})], 4)
        self.assertEquals(npp.polynomials[2].degree, (2, 3))
        self.assertEquals(npp.polynomials[2].c, 3)


if __name__ == "__main__":
    unittest.main()
