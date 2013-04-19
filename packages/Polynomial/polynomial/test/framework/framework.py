#!/usr/bin/python
# -*- coding: utf8
"""
testing diff, set0ToVar and set1ToVar methods using SymPy
"""
import formatter
from random import seed, random
from datetime import datetime
from sympy import Symbol, diff
import unittest
import math
import multiindex

EPS = 1E-6

seed(datetime.now())


class PolynomialToolsTestCase(unittest.TestCase):
    def doTestDiff(self, expression, diffVar, vars, testPointsCount=20):
        for v in vars:
            var = formatter.format(v, formatter.PYTHON)
            exec ("%s = Symbol('%s')" % (var, var))

        testPoints = list()
        for i in xrange(0, testPointsCount):
            subs = dict()
            for v in vars:
                var = formatter.format(v, formatter.PYTHON)
                exec ("subs[%s] = %s" % (var, random()))
            testPoints.append(subs)

        sDiff = eval('diff(%s,%s)' % (formatter.format(expression, 'PYTHON'),  formatter.format(diffVar, formatter.PYTHON)))
        myDiff = eval('+'.join(formatter.format(expression.diff(diffVar), 'PYTHON')))

        print 'testing diff:', formatter.format(expression, 'HUMAN')
        for subs in testPoints:
            sResult = sDiff.evalf(subs=subs)
            myResult = myDiff.evalf(subs=subs)
            print 'sympy:', sResult, 'my:', myResult
            self.assertTrue(math.fabs(sResult - myResult) <= EPS)

    def doTestSetNtoVar(self, expression, varToSet, n, vars, testPointsCount=20):
        for v in vars:
            var = formatter.format(v, formatter.PYTHON)
            exec ("%s = Symbol('%s')" % (var, var))

        testPoints = list()
        for i in xrange(0, testPointsCount):
            subs = dict()
            for v in vars:
                var = formatter.format(v, formatter.PYTHON)
                exec ("subs[%s] = %s" % (var, n if v == varToSet else random()))
            testPoints.append(subs)

        sResExpr = eval('%s' % (formatter.format(expression, 'PYTHON')))
        myResExpr = eval(
            formatter.format(expression.set1toVar(varToSet) if n == 1 else expression.set0toVar(varToSet), 'PYTHON'))

        print 'testing set%sToVar:' % n, formatter.format(expression, 'HUMAN')
        for subs in testPoints:
            sResult = sResExpr.evalf(subs=subs)
            myResult = myResExpr.evalf(subs=subs)
            print 'sympy:', sResult, 'my:', myResult
            self.assertTrue(math.fabs(sResult - myResult) <= EPS, 'oooops %s and %s' % (sResExpr, myResExpr))

    def doTestSet1toVar(self, expression, varToSet, vars, testPointsCount=20):
        self.doTestSetNtoVar(expression, varToSet, 1, vars, testPointsCount)

    def doTestSet0toVar(self, expression, varToSet, vars, testPointsCount=20):
        self.doTestSetNtoVar(expression, varToSet, 0, vars, testPointsCount)


