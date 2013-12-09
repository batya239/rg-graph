__author__ = 'gleb'

import unittest
import math

import graphine
import pole_extractor.diagram_calculator


class TestExpansionValues(unittest.TestCase):
    def testOneLoop(self):
        e1 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e11-e-'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertTrue(e1[-1][0] - e1[-1][1] <= -1.0 / 6.0 <= e1[-1][0] + e1[-1][1])
        self.assertTrue(e1[0][0] - e1[0][1] <= 0.25 <= e1[0][0] + e1[0][1])
        self.assertTrue(e1[1][0] - e1[1][1] <= -1.0 / 12.0 - math.pi**2 / 36.0 <= e1[1][0] + e1[1][1])

        e2 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e2-e-'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertTrue(e2[-1][0] - e2[-1][1] <= 0.5 <= e2[-1][0] + e2[-1][1])
        self.assertTrue(e2[0][0] - e2[0][1] <= -0.75 <= e2[0][0] + e2[0][1])
        self.assertTrue(e2[1][0] - e2[1][1] <= math.pi**2 / 12.0 + 0.25 <= e2[1][0] + e2[1][1])

    def testTwoLoops(self):
        e3 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-23-3-e-'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertTrue(e3[-2][0] - e3[-2][1] <= -1.0 / 12.0 <= e3[-2][0] + e3[-2][1])
        self.assertTrue(e3[-1][0] - e3[-1][1] <= 7.0 / 36.0 <= e3[-1][0] + e3[-1][1])

        e4 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-33--'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertTrue(e4[-2][0] - e4[-2][1] <= 1.0 / 72.0 <= e4[-2][0] + e4[-2][1])
        self.assertTrue(e4[-1][0] - e4[-1][1] <= 23.0 / 432.0 <= e4[-1][0] + e4[-1][1])

        e5 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-34-4-e-'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertTrue(e5[-2][0] - e5[-2][1] <= 0.125 <= e5[-2][0] + e5[-2][1])
        self.assertTrue(e5[-1][0] - e5[-1][1] <= -0.3125 <= e5[-1][0] + e5[-1][1])

        e6 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-e4-44--'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertTrue(e6[-2][0] - e6[-2][1] <= -1.0 / 24.0 <= e6[-2][0] + e6[-2][1])
        self.assertTrue(e6[-1][0] - e6[-1][1] <= -0.0625 <= e6[-1][0] + e6[-1][1])

        e7 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-34-34-e-e-'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertTrue(e7[-1][0] - e7[-1][1] <= 0.25 <= e7[-1][0] + e7[-1][1])
