#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dimas'

import unittest

import multiindex
import polynomial
import polynomial_product
import eps_number
import pole_extractor
import formatter


class PoleExtractorTest(unittest.TestCase):
    def test_eye(self):
        #p1 = (1 + u2 + u2*u3)**(-2*eps)
        p1 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({2: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 3: 1}): 1}, degree=eps_number.epsNumber((0, -2)))
        #p2 = (1 + u3 + u2*u3)**(eps - 2)
        p2 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({3: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 3: 1}): 1}, degree=eps_number.epsNumber((-2, 1)))
        #p3 = (u2)**(eps - 1)
        p3 = polynomial.Polynomial({multiindex.MultiIndex({2: 1}): 1}, degree=eps_number.epsNumber((-1, 1)))
        pp = polynomial_product.PolynomialProduct([p1, p2, p3])
        #raw dict
        extracted = pole_extractor.extract_poles_and_eps_series(pp, 2)
        # дикт, где значения уже в отформатированном виде
        formatted_dict = formatter.formatPoleExtracting(extracted).get(-1, None)
        self.assertEqual(formatted_dict, [('(pow(1+u3, -2))', ['u3'])])

    def test_eye1(self):
        #p1 = u1**eps
        p1 = polynomial.Polynomial({multiindex.MultiIndex({1: 1}): 1}, degree=eps_number.epsNumber((0, 1)))
        #p2 = (1 + u1 + u1*u3)**(-2*eps)
        p2 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({1: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 3: 1}): 1}, degree=eps_number.epsNumber((0, -2)))
        #p3 = (1 + u3 + u2*u3)**(eps - 2)
        p3 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({3: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 3: 1}): 1}, degree=eps_number.epsNumber((-2, 1)))
        pp = polynomial_product.PolynomialProduct([p1, p2, p3])
        extracted = pole_extractor.extract_poles_and_eps_series(pp, 2)
        self.assertEqual(extracted.get(-1, None), None)

    def test_eye2(self):
        #p0 = u1
        p0 = polynomial.Polynomial({multiindex.MultiIndex({1: 1}): 1}, degree=eps_number.epsNumber(1))
        #p1 = u3**eps
        p1 = polynomial.Polynomial({multiindex.MultiIndex({3: 1}): 1}, degree=eps_number.epsNumber((0, 1)))
        #p2 = (1 + u1 + u1*u3)**(-2*eps)
        p2 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({1: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 3: 1}): 1}, degree=eps_number.epsNumber((0, -2)))
        #p3 = (1 + u3 + u2*u3)**(eps - 2)
        p3 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({3: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 3: 1}): 1}, degree=eps_number.epsNumber((-2, 1)))
        pp = polynomial_product.PolynomialProduct([p0, p1, p2, p3])
        extracted = pole_extractor.extract_poles_and_eps_series(pp, 2)
        self.assertEqual(extracted.get(-1, None), None)

    def test_watermelon(self):
        #p1 = (u1)**(-3+2*eps)
        p1 = polynomial.Polynomial({multiindex.MultiIndex({1: 1}): 1}, degree=eps_number.epsNumber((-3, 2)))
        #p2 = (u2 + u3 + u2*u3)**(-3+eps)
        p2 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({3: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 3: 1}): 1}, degree=eps_number.epsNumber((-3, 1)))
        pp = polynomial_product.PolynomialProduct([p1, p2])
        #raw_dict
        extracted = pole_extractor.extract_poles_and_eps_series(pp, 2)
        print extracted
        self.assertEqual(extracted.get(-1, None), None)

    def test_watermelon2(self):
        #p1 = (1 + u2 + u2*u2)**(-3 + 2*eps)
        p1 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({3: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 3: 1}): 1}, degree=eps_number.epsNumber((-3, 1)))
        pass

    def test_zero_polynomials_expansion(self):
        #p1 = (u1)**(-2+2*eps)
        p1 = polynomial.Polynomial({multiindex.MultiIndex({1: 1}): 1}, degree=eps_number.epsNumber((-2, 2)))
        #p2 = (u4)**(-2+eps)
        p2 = polynomial.Polynomial({multiindex.MultiIndex({4: 1}): 1}, degree=eps_number.epsNumber((-2, 1)))
        #p3 = ((1+u1*u3+u1*u2+u1*u4*u5+u1*u4+u1)^(3-eps*3)
        p3 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({1: 1, 3: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 2: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 4: 1, 5: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 4: 1}): 1,
                                    multiindex.MultiIndex({1: 1}): 1}, degree=eps_number.epsNumber((3, -3)))
        #p4 = ((1+u1*u3*u5+u1*u2+u1*u2*u5+u2*u5+u1*u3+u3+u2+u1*u4*u5+u4*u5+u5+u3*u5)^(-3+eps))
        p4 = polynomial.Polynomial({multiindex.CONST: 1,
                                    multiindex.MultiIndex({1: 1, 3: 1, 5: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 2: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 2: 1, 5: 1}): 1,
                                    multiindex.MultiIndex({2: 1, 5: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 3: 1}): 1,
                                    multiindex.MultiIndex({3: 1}): 1,
                                    multiindex.MultiIndex({2: 1}): 1,
                                    multiindex.MultiIndex({1: 1, 4: 1, 5: 1}): 1,
                                    multiindex.MultiIndex({4: 1, 5: 1}): 1,
                                    multiindex.MultiIndex({5: 1}): 1,
                                    multiindex.MultiIndex({3: 1, 5: 1}): 1}, degree=eps_number.epsNumber((-3, 1)))
        pp = polynomial_product.PolynomialProduct([p1, p2, p3, p4])
        extracted = pole_extractor.extract_poles_and_eps_series(pp, 2)
         print extracted
        formatted_dict = formatter.formatPoleExtracting(extracted)
        print formatted_dict

if __name__ == "__main__":
    unittest.main()
