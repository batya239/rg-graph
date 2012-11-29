#!/usr/bin/python
# -*- coding: utf8
from string import find
import unittest
from multiindex import MultiIndex
from polynomial import Polynomial
from polynomial_product import PolynomialProduct

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

pp = PolynomialProduct({p1, p2})

class PolynomialProductTestCase(unittest.TestCase):
    def testSet0ToVar(self):
        self.assertTrue(pp.set0toVar(1).isZero())
        self.assertIn(pp.set0toVar(2).__repr__(), {'((3+eps*0)(6*(x_1^1)(x_4^2)(x_5^2))^(2+eps*3))*((3+eps*1)(4*1+5*(x_1^1)(x_5^2))^(1+eps*2))', '((3+eps*1)(4*1+5*(x_1^1)(x_5^2))^(1+eps*2))*((3+eps*0)(6*(x_1^1)(x_4^2)(x_5^2))^(2+eps*3))'})
        self.assertTrue(pp.set0toVar(5).isZero())

    def testSet1ToVar(self):
        self.assertIn(pp.set1toVar(1).__repr__(), {'((3+eps*1)(4*1+3*(x_2^4)(x_3^1)(x_4^4)+5*(x_5^2))^(1+eps*2))*((3+eps*0)(4*(x_2^4)(x_3^1)(x_5^1)+6*(x_4^2)(x_5^2))^(2+eps*3))', '((3+eps*0)(4*(x_2^4)(x_3^1)(x_5^1)+6*(x_4^2)(x_5^2))^(2+eps*3))*((3+eps*1)(4*1+3*(x_2^4)(x_3^1)(x_4^4)+5*(x_5^2))^(1+eps*2))'})
        self.assertIn(pp.set1toVar(1).set1toVar(5).__repr__(), {'((3+eps*1)(9*1+3*(x_2^4)(x_3^1)(x_4^4))^(1+eps*2))*((3+eps*0)(4*(x_2^4)(x_3^1)+6*(x_4^2))^(2+eps*3))', '((3+eps*0)(4*(x_2^4)(x_3^1)+6*(x_4^2))^(2+eps*3))*((3+eps*1)(9*1+3*(x_2^4)(x_3^1)(x_4^4))^(1+eps*2))'})

    def testDiff(self):
        self.assertTrue(find(pp.diff(2).__repr__(), '(6+eps*9)(16*(x_1^1)(x_2^3)(x_3^1)(x_5^1))^(1+eps*3)') > -1)

    def testStretch(self):
        self.assertTrue(find(pp.stretch(1, [2, 3, 7, 8]).__repr__(), '(3+eps*1)(4*1+5*(x_1^1)(x_5^2)+3*(x_1^8)(x_2^4)(x_3^1)(x_4^4))^(1+eps*2)') > -1)

    def testEpsExpansion(self):
        print pp.epsExpansion(3)[0].__repr__()
        print pp.epsExpansion(3)[1][0]
        print pp.epsExpansion(3)[1][1]
        print pp.epsExpansion(3)[1][2]
        print pp.epsExpansion(3)[1][3]


if __name__ == "__main__":
    unittest.main()
