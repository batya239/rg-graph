#!/usr/bin/python
__author__ = 'gleb'

import unittest
from pole_extractor import expansion_calculation as ec
from pole_extractor import adjacency_combinatorics as ac
from pole_extractor import feynman_construction as fc
import polynomial


def unique(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]


loops_phi4 = {
    'e111-e-':  2,
    'ee11-22-ee-': 2,
    'ee12-e22-e-': 2,
    'e112-22-e-': 3,
    'ee11-22-33-ee-': 3,
    'ee11-23-e33-e-': 3,
    'ee12-ee3-333--': 3,
    'ee12-e33-e33--': 3,
    'e112-e3-e33-e-': 3,
    'ee12-e23-33-e-': 3,
    'e123-e23-e3-e-': 3,
    'ee12-223-3-ee-': 3
}

connectivity_lists_phi4 = {
    'e111-e-':  [[-1, 0], [0, 1], [0, 1], [0, 1], [-1, 1]],
    'ee11-22-ee-': [[-1, 0], [-1, 0], [-1, 1], [-1, 1], [0, 2], [0, 2], [1, 2], [1, 2]],
    'ee12-e22-e-': [[-1, 0], [-1, 0], [-1, 1], [-1, 2], [0, 2], [0, 1], [1, 2], [1, 2]],
    'e112-22-e-': [[-1, 0], [-1, 1], [0, 2], [0, 2], [1, 2], [1, 2], [0, 1]],
    'ee11-22-33-ee-': [[-1, 0], [-1, 0], [-1, 1], [-1, 1], [0, 2], [0, 2], [1, 3], [1, 3], [2, 3], [2, 3]],
    'ee11-23-e33-e-': [[-1, 0], [-1, 0], [0, 1], [0, 1], [1, 2], [1, 3], [2, 3], [2, 3], [-1, 2], [-1, 3]],
    'ee12-ee3-333--': [[-1, 0], [-1, 0], [-1, 1], [-1, 1], [0, 1], [0, 2], [1, 3], [2, 3], [2, 3], [2, 3]],
    'ee12-e33-e33--': [[-1, 0], [-1, 0], [-1, 1], [-1, 2], [0, 1], [0, 2], [1, 3], [1, 3], [2, 3], [2, 3]],
    'e112-e3-e33-e-': [[-1, 0], [-1, 1], [-1, 2], [-1, 3], [0, 1], [0, 1], [2, 3], [2, 3], [0, 2], [1, 3]],
    'ee12-e23-33-e-': [[-1, 0], [-1, 0], [0, 1], [0, 2], [1, 2], [-1, 2], [1, 3], [1, 3], [2, 3], [-1, 3]],
    'e123-e23-e3-e-': [[-1, 0], [-1, 1], [-1, 2], [-1, 3], [0, 1], [0, 2], [0, 3], [1, 3], [1, 2], [2, 3]],
    'ee12-223-3-ee-': [[-1, 0], [-1, 0], [-1, 1], [-1, 1], [0, 2], [0, 3], [1, 2], [1, 3], [2, 3], [2, 3]]
}

determinants_phi4 = {
    'e111-e-':  [[1, 2], [1, 3], [2, 3]],
    'ee11-22-ee-': [[3, 5], ],
    'ee12-e22-e-': [[3, 5], [3, 6], [5, 6]],
    'e112-22-e-': [[1, 2, 4], [1, 2, 5], [1, 3, 4], [1, 3, 5], [1, 4, 5], [2, 3, 4], [2, 3, 5], [2, 4, 5]],
    'ee11-22-33-ee-': [[3, 5, 7], ],
    'ee11-23-e33-e-': [[3, 5, 7], [3, 5, 8], [3, 7, 8]],
    'ee12-ee3-333--': [[6, 7, 8], [6, 7, 9], [6, 8, 9], [7, 8, 9]],
    'ee12-e33-e33--': [[3, 5, 8], [3, 5, 9], [3, 6, 8], [3, 6, 9], [5, 6, 8], [5, 6, 9], [5, 8, 9], [6, 8, 9]],
    'e112-e3-e33-e-': [[1, 2, 7], [1, 2, 8], [1, 5, 7], [1, 5, 8], [1, 7, 8], [2, 5, 7], [2, 5, 8], [2, 7, 8]],
    'ee12-e23-33-e-': [[3, 5, 7], [3, 5, 8], [3, 6, 7], [3, 6, 8], [3, 7, 8], [5, 6, 7], [5, 6, 8], [5, 7, 8]],
    'e123-e23-e3-e-': [[1, 2, 5], [1, 2, 6], [1, 2, 8], [1, 3, 5], [1, 3, 6], [1, 3, 8], [1, 5, 8], [1, 6, 8],
                      [2, 3, 5], [2, 3, 6], [2, 3, 8], [2, 5, 6], [2, 6, 8], [3, 5, 6], [3, 5, 8], [5, 6, 8]],
    'ee12-223-3-ee-': [[3, 4, 5], [3, 4, 7], [3, 5, 7], [4, 5, 7]]
}

numerators_phi4 = {
    'e111-e-':  [],
    'ee11-22-ee-': [3, 5],
    'ee12-e22-e-': [3, ],
    'e112-22-e-': [],
    'ee11-22-33-ee-': [3, 5, 7],
    'ee11-23-e33-e-': [3, 5],
    'ee12-ee3-333--': [6, 6],
    'ee12-e33-e33--': [3, ],
    'e112-e3-e33-e-': [5, ],
    'ee12-e23-33-e-': [3, ],
    'e123-e23-e3-e-': [],
    'ee12-223-3-ee-': [3, 7]
}


class TestDetGenerator(unittest.TestCase):
    """
    Remember: enumeration of edge-according Feynman parameters is in the same order as enumeration of edges in
    Nickel's nomenclature
    """
    knownValuesPhi3 = (
        (2, [[-1, 2], [-1, 3], [-1, 4], [0, 1], [1, 0], [2, 0], [3, 2], [4, 3], [1, 4]], [[6, 7], [6, 8], [7, 8]]),
        (2, [[-1, 2], [-1, 3], [-1, 4], [0, 1], [0, 4], [1, 4], [3, 2], [1, 3], [0, 2]], [[4, 5], [4, 7], [5, 7]]),
        (2, [[-1, 2], [-1, 3], [-1, 4], [0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4]], [[2, 5], [2, 6], [5, 6]]),
        (2, [[0, 1], [0, 1], [0, 1]], [[0, 1], [0, 2], [1, 2]]),
        (3, [[-1, 0], [-1, 2], [-1, 5], [0, 1], [0, 4], [1, 3], [1, 2], [3, 4], [3, 6], [2, 6], [5, 6], [4, 5]],
         [[2, 3, 5], [2, 3, 11], [2, 3, 7], [2, 5, 9], [2, 9, 11], [2, 7, 9], [2, 5, 7], [2, 7, 11], [3, 5, 9],
          [3, 9, 11], [3, 7, 9], [3, 5, 11], [3, 7, 11], [5, 9, 11], [5, 7, 9], [5, 7, 11]])
    )

    def test_known_values_phi3(self):
        for loops, diag, det in self.knownValuesPhi3:
            info = ac.graph_info(diag)
            result = fc.determinant(info)
            self.assertEqual(det, result)

    def test_phi4(self):
        for k in determinants_phi4.keys():
            c_list = connectivity_lists_phi4[k]

            info = ac.graph_info(c_list)
            det1 = sorted(map(lambda x: sorted(x), fc.determinant(info)))
            det2 = sorted(map(lambda x: sorted(x), determinants_phi4[k]))
            #print k
            self.assertEqual(det1, det2)


class TestNumGenerator(unittest.TestCase):
    """
    """
    def test_phi4(self):
        for k in numerators_phi4.keys():
            c_list = connectivity_lists_phi4[k]

            info = ac.graph_info(c_list)
            num1 = sorted(fc.numerator(info))
            num2 = sorted(numerators_phi4[k])
            self.assertEqual(num1, num2)

"""
class TestCLaws(unittest.TestCase):

    def test_conservation_laws(self):
        for k in connectivity_lists_phi4.keys():
            nr_laws = ac.nr_conservation_laws(connectivity_lists_phi4[k])
            laws = ac.conservation_laws(connectivity_lists_phi4[k])
            short_laws = [x for x in laws if len(x) <= loops_phi4[k]]
            #print laws
            self.assertEqual(short_laws, nr_laws)
"""


class TestDiagramInfo(unittest.TestCase):
    """
    """
    def test_nickel(self):
        for k in connectivity_lists_phi4.keys():
            self.assertEqual(ac.graph_info(connectivity_lists_phi4[k])['nickel label'], k)

    def test_loops(self):
        for k in connectivity_lists_phi4.keys():
            self.assertEqual(ac.graph_info(k)['loops'], loops_phi4[k])


class TestEpsExpansion(unittest.TestCase):
    """
    """
    def test_parent(self):
        test_dict = {1: 2, 3: 4, 5: 6}
        e1 = ec.EpsExpansion(test_dict)
        self.assertEqual(sorted(e1.keys()), sorted(test_dict.keys()))
        self.assertEqual(e1[1], test_dict[1])
        self.assertEqual(e1[3], test_dict[3])
        self.assertEqual(e1[5], test_dict[5])
        e1.mul_by_eps_in(-2)
        self.assertEqual(e1.to_dict(), {-1: 2, 1: 4, 3: 6})

    def test_num_exp(self):
        e1 = ec.NumEpsExpansion({-1: [5, 0.01], 0: [-10, 0.1], 1: [2, 0.1], 2: [3, 0.1]})
        e2 = ec.NumEpsExpansion({1: [4, 1], 2: [20, 2], 3: [1, 0.01], 4: [3, 0.01]})
        e3 = ec.NumEpsExpansion({0: [1, 0.01], 1: [1, 0.01], 2: [1, 0.01], 3: [1, 0.01]})
        e4 = ec.NumEpsExpansion({-3: [1, 0.01], -2: [1, 0.01], -1: [1, 0.01], 0: [1, 0.01]})
        self.assertEqual((e1 + e2).to_dict(), {-1: [5, 0.01], 0: [-10, 0.1], 1: [6, 1.1],
                                               2: [23, 2.1], 3: [1, 0.01], 4: [3, 0.01]})
        self.assertEqual((e1 * e2).to_dict(), {0: [20.0, 5.05], 1: [60.0, 0.7200000000000006], 2: [-187.0, -15.2399],
                                               3: [57.0, 9.7811], })
        self.assertEqual((e3 * e4).to_dict(), {0: [4.0, 0.0804], -2: [2.0, 0.0402], -3: [1.0, 0.0201],
                                               -1: [3.0, 0.0603]})
        e2.merge(e1)
        self.assertEqual(e2.to_dict(), {-1: [5, 0.01], 0: [-10, 0.1], 1: [2, 0.1], 2: [3, 0.1], 3: [1, 0.01],
                                        4: [3, 0.01]})
        e5 = e3 + e4
        e5.principal_part()
        self.assertEqual(e5.to_dict(), {-3: [1, 0.01], -2: [1, 0.01], -1: [1, 0.01], })
        e3.stretch(5)
        e4.stretch(5)
        self.assertEqual(e3.to_dict(), {0: [1, 0.01], 1: [5, 0.05], 2: [25, 0.25], 3: [125, 1.25]})
        self.assertEqual(e4.to_dict(), {-3: [0.008, 0.00008], -2: [0.04, 0.0004], -1: [0.2, 0.002], 0: [1, 0.01]})

    def test_poly_exp(self):
        test_dict1 = dict()
        test_dict2 = dict()

        for i in list(xrange(-2, 4)):
            test_dict1[i] = [polynomial.poly([(1, [1]), (1, [2])], degree=i)] * abs(i)
        for i in list(xrange(2, 6)):
            test_dict2[i] = [polynomial.poly([(1, [3]), (1, [4])], degree=i)] * abs(i)
        e1 = ec.PolyEpsExpansion(test_dict1)
        e2 = ec.PolyEpsExpansion(test_dict2)
        e3 = e1 + e2

        for k in (e1 + e2).keys():
            l = 0
            if k in e1.keys():
                l += abs(k)
            if k in e2.keys():
                l += abs(k)
            self.assertEqual(l, len(e3[k]))
        self.assertEqual(sorted(e3.keys()), sorted(unique(e1.keys() + e2.keys())))


if __name__ == '__main__':
    unittest.main()