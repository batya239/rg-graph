#!/usr/bin/python
# -*- coding: utf8

__author__ = 'kirienko'

import unittest
from uncertSeries import Series
from uncertainties import ufloat


class SeriesOperationsTestCase(unittest.TestCase):
    def testAdd(self):
        z1 = Series(2, {0: ufloat(1, 0.3), 1: ufloat(2, .003)})
        z2 = Series(3, {0: ufloat(-1, 0.4), 1: ufloat(-2, .004), 2: ufloat(999, .1)})
        z3 = Series(2, {0: ufloat(0, 0.5), 1: ufloat(0, .005)})
        self.assertEqual(z1 + z2, z3)


if __name__ == "__main__":
    unittest.main()