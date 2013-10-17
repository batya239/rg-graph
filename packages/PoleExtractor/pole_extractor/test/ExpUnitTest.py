__author__ = 'gleb'

__author__ = 'gleb'

import unittest
import polynomial
import pole_extractor.numcalc
import pole_extractor.expansion


class TestAnalyticalCont(unittest.TestCase):
    """
    """
    def test_principal_part(self):
        return


class TestNumericCalculation(unittest.TestCase):
    """
    """
    def test_expansion1(self):
        for a in range(-5, -1):
            b = 4
            toIndex = 5

            p1 = polynomial.poly([(1, [1, ])], degree=(a, b))
            p2base = [(1, []), ]
            for i in range(1, -a + 1):
                p2base.append((1, [1]*i))
            p2 = polynomial.poly(p2base)

            polynomial_expansion = pole_extractor.expansion.extract_poles(p1 * p2, toIndex)
            integrated_exp = pole_extractor.numcalc.compute_exp_via_CUBA(polynomial_expansion)

            analytical_exp = {-1: float(b) ** (-1)}
            for k in range(toIndex + 1):
                analytical_exp[k] = 1
                for i in range(a + 1, 0):
                    analytical_exp[k] += i ** (-(k + 1))
                analytical_exp[k] *= (-b) ** k

            for k in sorted(integrated_exp.keys()):
                self.assertGreaterEqual(analytical_exp[k], integrated_exp[k][0] - integrated_exp[k][1])
                self.assertGreaterEqual(integrated_exp[k][0] + integrated_exp[k][1], analytical_exp[k])


class TestNumExpansion(unittest.TestCase):
    """
    """


if __name__ == '__main__':
    unittest.main()