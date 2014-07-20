#!/usr/bin/python

from uncertSeries import Series, Series2, Order
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


class TestSeries2(unittest.TestCase):
    def testInit(self):
        ## zero series
        s = Series2()
        self.assertEqual(s.order, False)
        self.assertEqual(s.name, 'g')
        self.assertEqual(s.gSeries,{0:0})
        s1 = Series2({1:1.})
        self.assertEqual(s1.order, False)
        self.assertEqual(s1.name, 'g')
        self.assertEqual(s1.gSeries,{1:1})


    def testLessThan(self):
        pass

    def testAdd(self):
        z = Series2()
        s1 = Series2({1:1})
        s2 = Series2({1:1,2:1})
        O = Order(2)
        sum1 = z + s1
        self.assertEqual(sum1.gSeries,{0:0, 1:1})
        self.assertEqual(sum1.order,False)
        sum2 = s1 + s2
        self.assertEqual(sum2.gSeries, {1:2, 2:1})
        self.assertEqual(sum2.order, False)
        sum3 = z+s1+s2
        self.assertEqual(sum3.gSeries,{0:0, 1:2, 2:1})
        sum4 = z+s1+s2 + O
        self.assertEqual(sum4.gSeries,{0:0, 1:2, 2:None})
        self.assertEqual(sum4.order, True)
        sum5 = z+s1+(s2 + O)
        self.assertEqual(sum5.gSeries,{0:0, 1:2, 2:None})
        self.assertEqual(sum5.order, True)




if __name__ == "__main__":
    unittest.main()