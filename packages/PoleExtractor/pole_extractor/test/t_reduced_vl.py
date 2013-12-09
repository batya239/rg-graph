__author__ = 'gleb'

import unittest
import pole_extractor.reduced_vl
import graphine

# phi^3 diagrams:
labels_vloops = ('111--', '112-3-33--', '123-23-3--')
labels_2tails = ('e12-e3-33--', 'e12-23-3-e-',
                 'e12-34-35-e-55--', 'e12-23-4-e5-55--', 'e12-23-4-45-5-e-',
                 'e12-e3-34-5-55--', 'e12-33-44-5-5-e-', 'e12-e3-44-55-5--',
                 'e12-34-35-4-5-e-', 'e12-34-34-5-5-e-', 'e12-e3-45-45-5--')
labels_3tails = ('e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-',
                 'e12-33-45-6-e6-e6--', 'e12-23-4-56-56-e-e-', 'e12-e3-45-46-e-66--',
                 'e12-23-4-e5-e6-66--', 'e12-23-4-e5-56-6-e-', 'e12-e3-44-56-5-6-e-',
                 'e12-e3-34-5-e6-66--', 'e12-e3-34-5-56-6-e-', 'e12-e3-e4-45-6-66--',
                 'e12-e3-44-55-6-6-e-', 'e12-e3-e4-55-66-6--', 'e12-e3-45-46-5-6-e-',
                 'e12-e3-45-45-6-6-e-', 'e12-e3-e4-56-56-6--', 'e12-34-56-e5-e6-6--',
                 'e12-34-35-6-e5-6-e-', 'e12-34-35-6-e6-e6--')


class TestReducedVacuumLoop(unittest.TestCase):
    def setUp(self):
        # 2-tailed diagrams on zero momenta
        self.subjects1 = {l: pole_extractor.reduced_vl.ReducedVacuumLoop.fromGraphineGraph(graphine.Graph.fromStr(l),
                                                                                           zero_momenta=True)
                          for l in labels_2tails}
        # 2-tailed diagrams prepared for calculating d/dp^2
        self.subjects2 = {l: pole_extractor.reduced_vl.ReducedVacuumLoop.fromGraphineGraph(graphine.Graph.fromStr(l),
                                                                                           zero_momenta=False)
                          for l in labels_2tails}

    def testEdgesNumber(self):
        """
        Check that on zero momenta and non-zero momenta we get same number of edges.
        """
        for k in self.subjects1.keys():
            self.assertEqual(sum(self.subjects1[k].edges_weights()),
                             sum(self.subjects2[k].edges_weights()))
