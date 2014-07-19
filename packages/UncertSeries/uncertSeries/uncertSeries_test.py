#!/usr/bin/python

from uncertSeries import Series
import unittest


class TestSeries(unittest.TestCase):
    def testInit(self):
        ## zero series
        s = Series()
        self.assertEqual(s.n,1)
        self.assertEqual(s.gSeries.keys(),[0])

    def testLessThan(self):
        pass

    def testAdd(self):
        z = Series()
        s1 = Series(n=2, d={1:1})
        s2 = Series(n=3, d={1:1,2:1})
        self.assertEqual((z+s1).gSeries.keys(),s1.gSeries.keys())
        self.assertEqual((s1+s2).gSeries.keys(),[0,1,2])
        self.assertEqual((z+s1+s2).gSeries.keys(),[0,1,2]) ## FIXME

    def testRAdd(self):
        pass

    def testSub(self):
        pass

    def testMul(self):
        pass

    def testRMul(self):
        pass

    def testNeg(self):
        pass

    def testInvert(self):
        pass

    def testDiv(self):
        pass

    def testRDiv(self):
        pass

    def testPow(self):
        pass

    def testStr(self):
        pass
class TestDiffSeries(unittest.TestCase):
    def testDiff(self):
        pass

class TestHelperSeries(unittest.TestCase):
    def testPPrint(self):
        pass

    def testSubs(self):
        pass

    def testSave(self):
        pass


if __name__ == "__main__":
    unittest.main()