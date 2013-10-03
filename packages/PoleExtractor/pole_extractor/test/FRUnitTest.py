__author__ = 'gleb'

import unittest
import known
import nickel
import pole_extractor.feynman_construction as feynman
import polynomial
import copy


def unite(seq):
    """
    turns sequence of sequences in sequence of elements of sequences, e.g.
    [[1, 2, 3], [4, 5], [6,]] -> [1, 2, 3, 4, 5, 6]
    """
    s = copy.deepcopy(seq)
    result = []
    while s:
        result.extend(s.pop(0))
    return result


class TestFeynman(unittest.TestCase):
    """
    """
    def setUp(self):
        self.feynman_reps = dict()
        for k in known.determinants.keys():
            self.feynman_reps[k] = feynman.Feynman(nickel.Nickel(string=k), theory=4)

    def test_integrand(self):
        for k in known.determinants.keys():
            det = polynomial.poly(map(lambda x: (1, x), known.determinants[k]), degree=(-2, 1))
            num = polynomial.poly([(1, known.numerators[k])], degree=1)
            #print self.feynman_reps[k]
            #if len(filter(lambda x: -1 in x, known.connectivity_lists[k])) == 2:
            #    print feynman.Feynman(nickel.Nickel(string=k), momentum_derivative=True, theory=4)
            self.assertEqual(self.feynman_reps[k]._integrand, det * num)

    def test_delta(self):
        for k in known.determinants.keys():
            all_vars = set(unite(known.determinants[k]))
            delta = polynomial.poly(map(lambda x: (1, [x]), list(all_vars)))
            self.assertEqual(self.feynman_reps[k]._delta_argument, delta)

    def test_gamma(self):
        for k in known.determinants.keys():
            internal_edges = len(filter(lambda x: -1 not in x, known.connectivity_lists[k]))
            self.assertEqual(self.feynman_reps[k]._gamma_coef1,(internal_edges - 2 * known.loops[k], known.loops[k]))
            self.assertEqual(self.feynman_reps[k]._gamma_coef2, (2, -1, known.loops[k]))

    #def test_inv_coef(self):

if __name__ == '__main__':
    unittest.main()