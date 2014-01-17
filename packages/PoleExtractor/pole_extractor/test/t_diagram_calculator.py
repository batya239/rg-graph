__author__ = 'gleb'

import unittest
import math

import graphine
import pole_extractor.diagram_calculator


class TestBaseValues(unittest.TestCase):
    def testOneLoop(self):
        e1 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e11-e-'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertEqual(e1[-1], -1.0 / 6.0)
        self.assertEqual(e1[0], 0.25)
        self.assertEqual(e1[1], -1.0 / 12.0 - math.pi**2 / 36.0)

        e2 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e2-e-'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertEqual(e2[-1], 0.5)
        self.assertEqual(e2[0], -0.75)
        self.assertEqual(e2[1], math.pi**2 / 12.0 + 0.25)

    def testTwoLoops(self):
        e3 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-23-3-e-'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertEqual(e3[-2], -1.0 / 12.0)
        self.assertEqual(e3[-1], 7.0 / 36.0)

        e4 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-33--'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertEqual(e4[-2], 1.0 / 72.0)
        self.assertEqual(e4[-1], 23.0 / 432.0)

        e5 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-34-4-e-'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertEqual(e5[-2], 0.125)
        self.assertEqual(e5[-1], -0.3125)

        e6 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-e4-44--'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertEqual(e6[-2], -1.0 / 24.0)
        self.assertEqual(e6[-1], -0.0625)

        e7 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-34-34-e-e-'),
                                                             rprime=False,
                                                             momentum_derivative=False)
        self.assertEqual(e7[-1], 0.25)


class TestRprValues(unittest.TestCase):
    def testOneLoop(self):
        e1 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e11-e-'),
                                                             rprime=True,
                                                             momentum_derivative=True)
        self.assertEqual(e1[-1], -1.0 / 6.0)
        self.assertEqual(e1[0], 0.25)
        self.assertEqual(e1[1], -1.0 / 12.0 - math.pi**2 / 36.0)

        e2 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e2-e-'),
                                                             rprime=True,
                                                             momentum_derivative=False)
        self.assertEqual(e2[-1], 0.5)
        self.assertEqual(e2[0], -0.75)
        self.assertEqual(e2[1], math.pi**2 / 12.0 + 0.25)

    def testTwoLoops(self):
        e1 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-23-3-e-'),
                                                             rprime=True,
                                                             momentum_derivative=True)
        self.assertEqual(e1[-2], 1.0 / 12.0)
        self.assertEqual(e1[-1], -2.0 / 36.0)

        e2 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-33--'),
                                                             rprime=True,
                                                             momentum_derivative=True)
        #self.assertEqual(e2[-2], -1.0 / 72.0)
        #self.assertEqual(e2[-1], 11.0 / 432.0)

        e3 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-34-4-e-'),
                                                             rprime=True,
                                                             momentum_derivative=False)
        self.assertEqual(e3[-2], -1.0 / 8.0)
        self.assertEqual(e3[-1], 1.0 / 16.0)

        e4 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e3-e4-44--'),
                                                             rprime=True,
                                                             momentum_derivative=False)
        self.assertEqual(e4[-2], 1.0 / 24.0)
        self.assertEqual(e4[-1], -7.0 / 144.0)

        e5 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-34-34-e-e-'),
                                                             rprime=True,
                                                             momentum_derivative=False)
        self.assertEqual(e5[-1], 0.25)