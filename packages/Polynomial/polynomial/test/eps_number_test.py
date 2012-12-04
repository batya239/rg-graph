#!/usr/bin/python
# -*- coding: utf8
import unittest
from eps_number import xPerm, EpsNumber, getCoefficients, epsNumber

class EpsNumberTestCase(unittest.TestCase):
    def testIt(self):
        sum =  EpsNumber(1, 2) + EpsNumber(3, 4)
        self.assertEquals(sum.a, 4)
        self.assertEquals(sum.b, 6)
        sub = EpsNumber(1, 2) - EpsNumber(3, 4)
        self.assertEquals(sub.a, -2)
        self.assertEquals(sub.b, -2)

    def testMultiply(self):
        self.assertEquals((3 * EpsNumber(1, 2)).a, 3)
        self.assertEquals((3 * EpsNumber(1, 2)).b, 6)

class EpsNumberAuxFunctionsTestCase(unittest.TestCase):
    def testGetCoefficients(self):
        c1 = getCoefficients([epsNumber((1, 2)), epsNumber(2), epsNumber((3, 4)), epsNumber(2)])
        print c1
        self.assertEquals(c1[0], 12)
        self.assertEquals(c1[1], 40.0)
        self.assertEquals(c1[2], 32.0)
        self.assertEquals(len(c1), 3)
        c2 = getCoefficients([epsNumber(3), epsNumber((2, 5)), epsNumber((3, 4))])
        print c2
        self.assertEquals(len(c2), 3)
        self.assertEquals(c2[0], 18)
        self.assertEquals(c2[1], 69)
        self.assertEquals(c2[2], 60)
        c3 = getCoefficients([epsNumber((0, 3)), epsNumber((2, 5)), epsNumber((3, 4))])
        print c3
        self.assertEquals(len(c3), 4)
        self.assertEquals(c3[0], 0)
        self.assertEquals(c3[1], 18)
        self.assertEquals(c3[2], 69.0)
        self.assertEquals(c3[3], 60)



if __name__ == "__main__":
    unittest.main()

