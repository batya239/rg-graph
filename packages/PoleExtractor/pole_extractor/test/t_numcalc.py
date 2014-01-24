__author__ = 'gleb'

import unittest

from pole_extractor import numcalc


class TestPrecisionNumbers(unittest.TestCase):
    def testEq(self):
        e1 = numcalc.PrecisionNumber(value=3, error=0.5)
        e2 = numcalc.PrecisionNumber(value=4, error=0.6)
        self.assertEqual(e1, e2)
        self.assertEqual(e2, e1)
        self.assertEqual(e1, 3)
        self.assertEqual(e1, 3.2)
        self.assertEqual(e2, 4.6)
        self.assertEqual(e2, 4)

    def testAdd(self):
        e1 = numcalc.PrecisionNumber(value=3, error=0.5)
        e2 = numcalc.PrecisionNumber(value=4, error=0.6)
        self.assertEqual(e1 + e2, 6)
        self.assertEqual(e1 + e2, 7)
        self.assertEqual(e1 + e2, 8)
        self.assertEqual(e1 + e2, numcalc.PrecisionNumber(value=10, error=2))
        self.assertEqual(e1 + e2, numcalc.PrecisionNumber(value=8, error=0.01))
        self.assertEqual(e1 + 2, 5)
        self.assertEqual(2 + e1, 5)
        self.assertEqual(e1 + 2.1, 5)
        self.assertEqual(2.1 + e1, 5)

    def testMul(self):
        e1 = numcalc.PrecisionNumber(value=3, error=0.5)
        e2 = numcalc.PrecisionNumber(value=4, error=0.6)
        self.assertEqual(e1 * e2, 12)


class TestNumEpsExpansion(unittest.TestCase):
    def testAdd(self):
        e1 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [2.0, 0.0], 2: [1.0, 0.0]}, precise=True)
        e2 = numcalc.NumEpsExpansion({1: [1.0, 0.0], 2: [1.0, 0.0]}, precise=True)
        e3 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [1.0, 0.0]}, precise=True)
        self.assertEqual(e2 + e3, e1)

        e4 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [2.0, 0.0], 2: [1.0, 0.0]})
        e5 = numcalc.NumEpsExpansion({3: [1.0, 0.0], 4: [2.0, 0.0], 5: [1.0, 0.0]})
        self.assertEqual(e4 + e5, e4)
        self.assertEqual(e5 + e4, e4)

        e4 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [2.0, 0.0], 2: [1.0, 0.0]})
        e5 = numcalc.NumEpsExpansion({3: [1.0, 0.0], 4: [2.0, 0.0], 5: [1.0, 0.0]}, precise=True)
        self.assertEqual(e4 + e5, e4)
        self.assertEqual(e5 + e4, e4)

        e6 = numcalc.NumEpsExpansion({-2: [1.0, 0.0], -1: [1.0, 0.0], 0: [1.0, 0.0], 1: [1.0, 0.0],
                                                     2: [1.0, 0.0], 3: [1.0, 0.0]})
        e7 = numcalc.NumEpsExpansion({0: [2.0, 0.0], 1: [2.0, 0.0], 2: [2.0, 0.0], 3: [2.0, 0.0]})
        e8 = numcalc.NumEpsExpansion({-2: [1.0, 0.0], -1: [1.0, 0.0], 0: [3.0, 0.0], 1: [3.0, 0.0],
                                                     2: [3.0, 0.0], 3: [3.0, 0.0]})
        self.assertEqual(e6 + e7, e8)
        self.assertEqual(e7 + e6, e8)

    def testMul(self):
        e1 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [2.0, 0.0], 2: [1.0, 0.0]}, precise=True)
        e2 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [1.0, 0.0]}, precise=True)
        self.assertEqual(e2 * e2, e1)

        e3 = numcalc.NumEpsExpansion({1: [2.0, 0.0], 2: [3.0, 0.0], 3: [4.0, 0.0]})
        e4 = numcalc.NumEpsExpansion({-1: [1.0, 0.0], -2: [-5.0, 0.0]}, precise=True)
        e5 = numcalc.NumEpsExpansion({-1: [-10.0, 0.0], 0: [-13.0, 0.0], 1: [-17.0, 0.0]})
        self.assertEqual(e3 * e4, e5)

    def testCut(self):
        e1 = numcalc.NumEpsExpansion({0: [1.0, 0.0], 1: [2.0, 0.0], 2: [1.0, 0.0]})
        e2 = numcalc.NumEpsExpansion({0: [1.0, 0.0]}, precise=True)
        self.assertEqual(e1.cut(1), e2)