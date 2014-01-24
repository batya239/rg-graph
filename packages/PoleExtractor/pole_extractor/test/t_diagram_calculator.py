__author__ = 'gleb'

import unittest
import math

import graphine
import pole_extractor.diagram_calculator


class TestBaseValuesPhi3(unittest.TestCase):
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

        e3 = pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e12-e2--'),
                                                             rprime=False,
                                                             momentum_derivative=True)
        self.assertEqual(e3[0], -1.0 / 12.0)
        self.assertEqual(e3[1], 0.125)
        self.assertEqual(e3[2], -math.pi**2 / 72.0 - 1.0 / 24.0)

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


class TestRprValuesPhi3(unittest.TestCase):
    """
    Vassiliev pg 415
    """
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
        self.assertEqual(e2[-2], -1.0 / 72.0)
        self.assertEqual(e2[-1], 11.0 / 432.0)

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


class TestBaseValuesPhi4(unittest.TestCase):
    def testOneLoop(self):
        e1 = 2.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-ee-'),
                                                                   rprime=False,
                                                                   momentum_derivative=False)
        self.assertEqual(e1[-1], 1.0)

    def testSimpleLoops(self):
        e1 = 2.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-ee-'),
                                                                   rprime=False,
                                                                   momentum_derivative=False)
        e3 = 4.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-22-ee-'),
                                                                   rprime=False,
                                                                   momentum_derivative=False)
        e3_check = e1 * e1
        self.assertEqual(e3[-2], e3_check[-2])
        self.assertEqual(e3[-1], e3_check[-1])
        self.assertEqual(e3[0], e3_check[0])
        self.assertEqual(e3[1], e3_check[1])
        self.assertEqual(e3[2], e3_check[2])
        self.assertEqual(e3[3], e3_check[3])

        e6 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-22-33-ee-'),
                                                                   rprime=False,
                                                                   momentum_derivative=False)
        e6_check = e1 * e1 * e1
        self.assertEqual(e6[-3], e6_check[-3])
        self.assertEqual(e6[-2], e6_check[-2])
        self.assertEqual(e6[-1], e6_check[-1])
        self.assertEqual(e6[0], e6_check[0])
        self.assertEqual(e6[1], e6_check[1])
        self.assertEqual(e6[2], e6_check[2])


class TestRprValuesPhi4(unittest.TestCase):
    """
    Vassiliev pg 277
    """
    def testOneLoop(self):
        e1 = 2.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-ee-'),
                                                                   rprime=False,
                                                                   momentum_derivative=False)
        self.assertEqual(e1[-1], 1.0)

    def testTwoLoops(self):
        e2 = 4.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e111-e-'),
                                                                   rprime=True,
                                                                   momentum_derivative=True)
        self.assertEqual(e2[-1], -0.25)

        e3 = 4.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-22-ee-'),
                                                                   rprime=True,
                                                                   momentum_derivative=False)
        self.assertEqual(e3[-2], -1.0)
        self.assertEqual(e3[-1], 0.0)

        e4 = 4.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee12-e22-e-'),
                                                                   rprime=True,
                                                                   momentum_derivative=False)
        self.assertEqual(e4[-2], -0.5)
        self.assertEqual(e4[-1], 0.5)

    def testThreeLoops(self):
        e5 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e112-22-e-'),
                                                                   rprime=True,
                                                                   momentum_derivative=True)
        self.assertEqual(e5[-2], 1.0 / 6.0)
        self.assertEqual(e5[-1], -1.0 / 12.0)

        e6 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-22-33-ee-'),
                                                                   rprime=True,
                                                                   momentum_derivative=False)
        self.assertEqual(e6[-3], 1.0)
        self.assertEqual(e6[-2], 0.0)
        self.assertEqual(e6[-1], 0.0)

        e7 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee11-23-e33-e-'),
                                                                   rprime=True,
                                                                   momentum_derivative=False)
        self.assertEqual(e7[-3], 0.5)
        self.assertEqual(e7[-2], -0.5)
        self.assertEqual(e7[-1], 0.0)

        e8 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee12-ee3-333--'),
                                                                   rprime=True,
                                                                   momentum_derivative=False)
        self.assertEqual(e8[-2], 1.0 / 6.0)
        self.assertEqual(e8[-1], -0.375)

        e9 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee12-e33-e33--'),
                                                                   rprime=True,
                                                                   momentum_derivative=False)
        self.assertEqual(e9[-3], 1.0 / 3.0)
        self.assertEqual(e9[-2], -1.0 / 3.0)
        self.assertEqual(e9[-1], -1.0 / 3.0)

        e10 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e112-e3-e33-e-'),
                                                                    rprime=True,
                                                                    momentum_derivative=False)
        self.assertEqual(e10[-3], 1.0 / 3.0)
        self.assertEqual(e10[-2], -1.0 / 3.0)
        self.assertEqual(e10[-1], -1.0 / 3.0)

        e11 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee12-e23-33-e-'),
                                                                    rprime=True,
                                                                    momentum_derivative=False)
        self.assertEqual(e11[-3], 1.0 / 6.0)
        self.assertEqual(e11[-2], -0.5)
        self.assertEqual(e11[-1], 2.0 / 3.0)

        e12 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('e123-e23-e3-e-'),
                                                                    rprime=True,
                                                                    momentum_derivative=False)
        self.assertEqual(e12[-1], 2.404113806)

        e13 = 8.0 * pole_extractor.diagram_calculator.get_expansion(graphine.Graph.fromStr('ee12-223-3-ee-'),
                                                                    rprime=True,
                                                                    momentum_derivative=False)
        self.assertEqual(e13[-3], 1.0 / 3.0)
        self.assertEqual(e13[-2], -2.0 / 3.0)
        self.assertEqual(e13[-1], 1.0 / 3.0)