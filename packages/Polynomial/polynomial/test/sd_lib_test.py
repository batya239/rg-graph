#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

import unittest

import polynomial
import sd_lib


class SectorPolyTestCase(unittest.TestCase):

    def testIt(self):
        sector = [(1, (2, 3)), (2, (3,))]
        poly1 = polynomial.poly([(1, [1, ]), (1, [2, ]), (1, [3, ])])
        poly1_res = polynomial.poly([(1, [1, ]), (1, [1, 2, ]), (1, [1, 2, 3, ])])
        self.assertEquals(sd_lib.sectorPoly(poly1, sector), poly1_res)
        sector = [(1, (2,)), (1, (3,))]
        poly1 = polynomial.poly([(1, [1, ]), (1, [2, ]), (1, [3, ])])
        poly1_res = polynomial.poly([(1, [1, ]), (1, [1, 2, ]), (1, [1, 3, ])])
        self.assertEquals(sd_lib.sectorPoly(poly1, sector), poly1_res)


class SectorDiagramTestCase(unittest.TestCase):
    def testSimpleSector(self):
        sector = [(1, (2, 3)), (2, (3,))]
        delta_arg = polynomial.poly([(1, [1, ]), (1, [2, ]), (1, [3, ])])
        expr = polynomial.poly([(1, [1, 2]), (1, [2, 3]), (1, [1, 3])], degree=(-2, 1)).toPolyProd()
        res = (polynomial.poly([(1, [1, 1, 2]), (1, [1, 1, 2, 2, 3]), (1, [1, 1, 2, 3])], degree=(-2, 1)).set1toVar(1)
               * polynomial.poly([(1, []), (1, [2, ]), (1, [2, 3, ])], degree=(1, -2))
               * polynomial.poly([(1, [2, ]), ])).simplify()
        self.assertEquals(sd_lib.sectorDiagram(expr, sector, delta_arg).simplify(), res)

    def testInvalidDeltaArg(self):
        sector = [(1, (2, 3)), (2, (3,))]
        delta_arg = polynomial.poly([(1, [1, ]), (1, [2, ])])
        expr = polynomial.poly([(1, [1, 2]), (1, [2, 3]), (1, [1, 3])], degree=(-2, 1)).toPolyProd()
        self.assertRaises(ValueError, sd_lib.sectorDiagram, expr, sector, delta_arg)
        self.assertRaises(ValueError, sd_lib.sectorDiagram, expr, sector)

    def testNotRemoveDelta(self):
        sector = [(1, (2, 3)), (2, (3,))]
        delta_arg = polynomial.poly([(1, [1, ]), (1, [2, ]), (1, [3, ])])
        expr = polynomial.poly([(1, [1, 2]), (1, [2, 3]), (1, [1, 3])], degree=(-2, 1)).toPolyProd()
        res = [(polynomial.poly([(1, [1, 1, 2]), (1, [1, 1, 2, 2, 3]), (1, [1, 1, 2, 3])], degree=(-2, 1))
               * polynomial.poly([(1, [1, 1, 2, ]), ])).simplify(),
               polynomial.poly([(1, [1, ]), (1, [1, 2, ]), (1, [1, 2, 3, ])])]
        ans = sd_lib.sectorDiagram(expr, sector, delta_arg, remove_delta=False)
        self.assertEquals(ans[0].simplify(), res[0])
        self.assertEquals(ans[1], res[1])

        res = (polynomial.poly([(1, [1, 1, 2]), (1, [1, 1, 2, 2, 3]), (1, [1, 1, 2, 3])], degree=(-2, 1))
               * polynomial.poly([(1, [1, 1, 2, ]), ])).simplify()
        self.assertEquals(sd_lib.sectorDiagram(expr, sector, remove_delta=False).simplify(), res)



if __name__ == "__main__":
    unittest.main()