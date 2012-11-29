#!/usr/bin/python
# -*- coding: utf8
import unittest
from eps_power import EpsPower

class EpsPowerTestCase(unittest.TestCase):
    def testIt(self):
        sum =  EpsPower(1, 2) + EpsPower(3, 4)
        self.assertEquals(sum.a, 4)
        self.assertEquals(sum.b, 6)
        sub = EpsPower(1, 2) - EpsPower(3, 4)
        self.assertEquals(sub.a, -2)
        self.assertEquals(sub.b, -2)

    def testMultiply(self):
        self.assertEquals((3 * EpsPower(1, 2)).a, 3)
        self.assertEquals((3 * EpsPower(1, 2)).b, 6)

if __name__ == "__main__":
    unittest.main()

