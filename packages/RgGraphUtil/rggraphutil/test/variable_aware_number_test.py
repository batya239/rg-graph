#!/usr/bin/python
# -*- coding: utf8
import unittest
import variable_aware_number as v_number

__author__ = 'daddy-bear'

varName = "eps"


class VariableAwareNumberTestCase(unittest.TestCase):
    def testIt(self):
        _sum = v_number.VariableAwareNumber(varName, 1, 2) + v_number.VariableAwareNumber(varName, 3, 4)
        self.assertEquals(_sum.a, 4)
        self.assertEquals(_sum.b, 6)
        sub = v_number.VariableAwareNumber(varName, 1, 2) - v_number.VariableAwareNumber(varName, 3, 4)
        self.assertEquals(sub.a, -2)
        self.assertEquals(sub.b, -2)
        neg = - v_number.VariableAwareNumber(varName, 1, 2)
        self.assertEquals(neg.a, -1)
        self.assertEquals(neg.b, -2)

    def testMultiply(self):
        self.assertEquals((3 * v_number.VariableAwareNumber(varName, 1, 2)).a, 3)
        self.assertEquals((3 * v_number.VariableAwareNumber(varName, 1, 2)).b, 6)


class VariableAwareNumberAuxFunctionsTestCase(unittest.TestCase):
    def testGetCoefficients(self):
        c1 = v_number.VariableAwareNumber.getPolynomialCoefficients([v_number.VariableAwareNumber.create(varName, (1, 2)),
                                                                     v_number.VariableAwareNumber.create(varName, 2),
                                                                     v_number.VariableAwareNumber.create(varName, (3, 4)),
                                                                     v_number.VariableAwareNumber.create(varName, 2)])
        print c1
        self.assertEquals(c1[0], 12)
        self.assertEquals(c1[1], 40.0)
        self.assertEquals(c1[2], 32.0)
        self.assertEquals(len(c1), 3)
        c2 = v_number.VariableAwareNumber.getPolynomialCoefficients([v_number.VariableAwareNumber.create(varName, 3),
                                                                     v_number.VariableAwareNumber.create(varName, (2, 5)),
                                                                     v_number.VariableAwareNumber.create(varName, (3, 4))])
        print c2
        self.assertEquals(len(c2), 3)
        self.assertEquals(c2[0], 18)
        self.assertEquals(c2[1], 69)
        self.assertEquals(c2[2], 60)
        c3 = v_number.VariableAwareNumber.getPolynomialCoefficients([v_number.VariableAwareNumber.create(varName, (0, 3)),
                                                                     v_number.VariableAwareNumber.create(varName, (2, 5)),
                                                                     v_number.VariableAwareNumber.create(varName, (3, 4))])
        print c3
        self.assertEquals(len(c3), 4)
        self.assertEquals(c3[0], 0)
        self.assertEquals(c3[1], 18)
        self.assertEquals(c3[2], 69.0)
        self.assertEquals(c3[3], 60)


if __name__ == "__main__":
    unittest.main()
