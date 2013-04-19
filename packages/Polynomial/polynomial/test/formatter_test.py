#!/usr/bin/python
# -*- coding: utf8
import unittest
import formatter
import multiindex
import polynomial

mi1_1 = multiindex.MultiIndex({1: 3, 2: 4, 4: 4, 3: 1})
c1_1 = 3
mi1_2 = multiindex.MultiIndex({1: 1, 5: 2})
c1_2 = 5
mi1_3 = multiindex.MultiIndex()
c1_3 = 4
p1 = polynomial.Polynomial({mi1_1: c1_1, mi1_2: c1_2, mi1_3: c1_3}, (1, 2), (3, 1))

mi2_1 = multiindex.MultiIndex({1: 1, 2: 4, 3: 1, 5: 1})
c2_1 = 4
mi2_2 = multiindex.MultiIndex({1: 1, 4: 2, 5: 2})
c2_2 = 6
p2 = polynomial.Polynomial({mi2_1: c2_1, mi2_2: c2_2}, (2, 3), (3, 0))

p3 = polynomial.Polynomial({mi2_2: 31}, (2, 3), (3, 0))

pp = p1 * p2

pp1 = p1 * p2 * p3

pp2 = p2 * p3 * p3


class PolynomialProductTestCase(unittest.TestCase):
    def testVarExtracting(self):
        p = formatter.formatWithExtractingNewVariables([pp, pp1], variableBasement="_B")
        self.assertEquals(len(p[1]), 2)
        self.assertEquals(p[1]["_B0"], formatter.format(p1))
        self.assertEquals(p[1]["_B1"], formatter.format(p2))

        p = formatter.formatWithExtractingNewVariables([pp2, pp1], variableBasement="_B")
        self.assertEquals('(_B1)*(_B0)*(_B0)', p[0][0])
        self.assertEquals(len(p[1]), 2)
        self.assertEquals(p[1]["_B0"], formatter.format(p3))
        self.assertEquals(p[1]["_B1"], formatter.format(p2))

    def testVarExtractingWithDict(self):
        t = formatter.formatWithExtractingNewVariables([pp, pp1], {"1": pp2}, variableBasement="_C",
                                                       exportType=formatter.CPP)
        self.assertEquals('(_C0)*(_C1)', t[0][0])
        self.assertEquals('(_C0)*(_C1)*(_C2)', t[0][1])
        self.assertEquals(1, len(t[1]))
        self.assertEquals('(_C1)*(_C2)*(_C2)', t[1]["1"])
        self.assertEquals(t[2]["_C0"], formatter.format(p1, exportType=formatter.CPP))
        self.assertEquals(t[2]["_C1"], formatter.format(p2, exportType=formatter.CPP))
        self.assertEquals(t[2]["_C2"], formatter.format(p3, exportType=formatter.CPP))

if __name__ == "__main__":
    unittest.main()
