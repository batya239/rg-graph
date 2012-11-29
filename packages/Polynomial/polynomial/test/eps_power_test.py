#!/usr/bin/python
# -*- coding: utf8
import unittest
from eps_power import EpsNumber

class EpsPowerTestCase(unittest.TestCase):
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

if __name__ == "__main__":
    unittest.main()

