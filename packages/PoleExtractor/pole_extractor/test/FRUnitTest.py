__author__ = 'gleb'

import unittest
import known
import nickel
import pole_extractor.feynman_construction as feynman
import polynomial


class TestFeynman(unittest.TestCase):
    """
    """
    def test_integrand(self):
        for k in known.determinants.keys():
            f = feynman.Feynman(nickel.Nickel(string=k), theory=4)
            det = polynomial.poly(map(lambda x: (1, x), known.determinants[k]), degree=(-2, 1))
            num = polynomial.poly([(1, known.numerators[k])], degree=1)
            self.assertEqual(f._integrand, det * num)

    #def test_gammas(self):

if __name__ == '__main__':
    unittest.main()