#!/usr/bin/python
# -*- coding: utf8
from string import find
import unittest
from multiindex import MultiIndex, CONST
from polynomial import Polynomial, poly
from framework.framework import PolynomialToolsTestCase
from polynomial_product import PolynomialProduct
from checkers import exactMonomial, coefficientIs, degreeIs

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
pp2 = p1 * p1

VARS = [1, 2, 3, 4, 5, 'eps']


class PolynomialProductTestCase(PolynomialToolsTestCase):
    def testDiv(self):
        self.assertEqual(pp / p1, p2.toPolyProd())
        self.assertEqual(((p1.toPolyProd() * 3) / Polynomial({CONST: 1}, 0, 3)), p1.toPolyProd())

    def testNoneEq(self):
        self.assertFalse(p1 is None)

    def testInit(self):
        p3 = poly([(1, [])])
        self.assertEquals(map(lambda x: x.isOne(), PolynomialProduct([p3]).polynomials), [True])

    def testCalculatePowerForVarIndex(self):
        self.assertEquals(pp.calcPower(2), 0)
        self.assertEquals(p1.calcPower(2), 0)
        self.assertEquals(p2.calcPower(1), (2, 3))
        self.assertEquals(pp.calcPower(1), (2, 3))

        mi2_1 = MultiIndex({1: 3, 2: 4, 3: 1, 5: 1})
        c2_1 = 4
        mi2_2 = MultiIndex({1: 2, 4: 2, 5: 2})
        c2_2 = 6
        _p2 = Polynomial({mi2_1: c2_1, mi2_2: c2_2}, (2, 3), (3, 0))
        _pp = p1 * _p2
        self.assertEquals(_pp.calcPower(1), (4, 6))

    def testDiff(self):
        self.doTestDiff(pp, 1, VARS)
        self.doTestDiff(pp, 2, VARS)
        self.doTestDiff(pp2, 2, VARS)
        self.doTestDiff(p1 * p2 * p1, 2, VARS)

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

    def testEpsExpansion2(self):
        a = poly([(1, [1, 2])]).toPolyProd()
        self.assertEquals(repr(a.epsExpansion(2)), "EpsExpansionResult(factor=((u1*u2)), main_expansion={0: [1], 1: [0], 2: [0]})")

    def testSimplifying(self):
        npp = pp.simplify()

        self.assertEquals(len(npp.polynomials), 4)
        self.assertTrue(npp.hasPolynomialWith().monomial(exactMonomial({1: 1}, 1)))
        self.assertTrue(npp.hasPolynomialWith(degreeIs((2, 3)).and_(coefficientIs(1))))
        self.assertTrue(npp.hasPolynomialWith(degreeIs((2, 3)).and_(coefficientIs(3)))
            .withMonomial(exactMonomial({2: 4, 3: 1}, 4)))
        pp1 = poly([(1, (2, 3)), (1, (1, 2, 'a0', 'a0')), (1, (1, 3, 'a1'))]).toPolyProd()
        pps = pp1.diff('a1')[0].simplify()
        self.assertEquals(len(pps), 2)
        pp1 = poly([(1, []), (1, [2, 3]), (1, [3]), (1, [2])])
        pp2 = poly([(3, []), (1, [2, 3]), (3, [3]), (2, [2])], degree=(-3, 1))
        self.assertEquals((pp1 * pp2).simplify(), pp1 * pp2)

        pp3 = (poly([(1, [1])]) * poly([(1, [1])], degree=-1)).simplify()

        # must be at least a product of a unit polynomials
        self.assertTrue(reduce(lambda x, y: x & y, map(lambda x: x.isOne(), pp3.polynomials)))
        # in fact it should be equal to 1, not 1*1
        self.assertEqual(map(lambda x: x.isOne(), pp3.polynomials), [True])

        pp3 = (poly([(1, [1])], degree=-1) * poly([(1, [1])]) * poly([(1, [1])])).simplify()

        self.assertEquals(pp3, poly([(1, [1])]).toPolyProd())


def testMull(self):
        pp0 = poly([(1, ('a0',))]).toPolyProd().set0toVar('a0')
        self.assertEquals(pp0 * pp, pp0)


if __name__ == "__main__":
    unittest.main()
