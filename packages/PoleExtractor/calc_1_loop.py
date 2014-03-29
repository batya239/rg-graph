__author__ = 'gleb'

from pole_extractor import diagram_calculator
from pole_extractor import numcalc
import graphine

# setting up all 1-loop expansions that
# can't be calculated w/ pole_extractor

for r in (True, False):
    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e11|e|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [0.5, 1e-08], 1: [-1.6449341, 1e-08],
                                                                2: [0.82246703, 1e-08], 3: [-1.8940657, 1e-08],
                                                                4: [0.94703283, 1e-08], 5: [-1.9711022, 1e-08],
                                                                6: [0.98555109, 1e-08], 7: [-1.992466, 1e-08],
                                                                8: [0.996233, 1e-08], -1: [-1.0, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e11|e|'),
                                     rprime=r,
                                     momentum_derivative=True,
                                     e=numcalc.NumEpsExpansion({0: [0.25, 1e-08], 1: [-0.35748901, 1e-08],
                                                                2: [0.41123352, 1e-08], 3: [-0.45275545, 1e-08],
                                                                4: [0.47351641, 1e-08], 5: [-0.48635584, 1e-08],
                                                                6: [0.49277555, 1e-08], 7: [-0.49633618, 1e-08],
                                                                8: [0.4981165, 1e-08], -1: [-0.16666667, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e2|e|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [-0.75, 1e-08], 1: [1.07246703, 1e-08],
                                                                2: [-1.2337006, 1e-08], 3: [1.3582663, 1e-08],
                                                                4: [-1.4205492, 1e-08], 5: [1.4590675, 1e-08],
                                                                6: [-1.4783266, 1e-08], 7: [1.4890085, 1e-08],
                                                                8: [-1.4943495, 1e-08], -1: [0.5, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e2||'),
                                     rprime=r,
                                     momentum_derivative=True,
                                     e=numcalc.NumEpsExpansion({0: [-0.08333333333, 1e-08], 1: [0.125, 1e-08],
                                                                2: [-0.1787445056, 1e-08], 3: [0.2056167584, 1e-08],
                                                                4: [-0.2263777244, 1e-08], 5: [0.2367582074, 1e-08],
                                                                6: [-0.2431779177, 1e-08], 7: [0.2463877728, 1e-08],
                                                                8: [-0.2481680913, 1e-08], 9: [0.2490582505, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e3|3||'),
                                     rprime=r,
                                     momentum_derivative=True,
                                     e=numcalc.NumEpsExpansion({0: [-0.025, 1e-08], 1: [0.0125, 1e-08],
                                                                2: [-0.016123352, 1e-08], 3: [0.0080616758, 1e-08],
                                                                4: [-0.0062282898, 1e-08], 5: [0.0031141449, 1e-08],
                                                                6: [-0.0019259131, 1e-08], 7: [0.00096295655, 1e-08],
                                                                8: [-0.00053409553, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|3|3|e|'),
                                     rprime=r,
                                     momentum_derivative=True,
                                     e=numcalc.NumEpsExpansion({0: [-0.03333333, 1E-8], 1: [0.016666667, 1E-8],
                                                                2: [-0.021497802, 1E-8], 3: [0.010748901, 1E-8],
                                                                4: [-0.008304386, 1E-8], 5: [0.004152193, 1E-8],
                                                                6: [-0.002567884, 1E-8]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|3|4|e4||'),
                                     rprime=r,
                                     momentum_derivative=True,
                                     e=numcalc.NumEpsExpansion({0: [-0.016666667, 1E-8], 1: [0.0, 0.0],
                                                                2: [-0.0065822344, 1E-8], 3: [0.0, 0.0],
                                                                4: [-0.0014649679, 1E-8], 5: [0.0, 0.0],
                                                                6: [-0.00024589376, 1E-8], 7: [0.0, 0.0],
                                                                8: [-0.000035078170, 1E-8]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e3|4|4||'),
                                     rprime=r,
                                     momentum_derivative=True,
                                     e=numcalc.NumEpsExpansion({0: [-0.011111111, 1E-8], 1: [0.0, 0.0],
                                                                2: [-0.0043881563, 1E-8], 3: [0.0, 0.0],
                                                                4: [-0.00097664528, 1E-8], 5: [0.0, 0.0],
                                                                6: [-0.00016392917, 1E-8], 7: [0.0, 0.0],
                                                                8: [-0.000023385447, 1E-8]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e3|e3|e|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [0.16666667, 1e-08], 1: [-0.25, 1e-08],
                                                                2: [0.35748901, 1e-08], 3: [-0.41123352, 1e-08],
                                                                4: [0.45275545, 1e-08], 5: [-0.47351641, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('ee11|ee|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [-0.5, 1e-08], 1: [0.8224670334, 1e-08],
                                                                2: [-0.8224670334, 1e-08], 3: [0.9470328295, 1e-08],
                                                                4: [-0.9470328295, 1e-08], 5: [0.9855510913, 1e-08],
                                                                6: [-0.9855510913, 1e-08], 7: [0.9962330019, 1e-08],
                                                                8: [-0.9962330019, 1e-08], -1: [0.5, 1e-08]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e3|e4|e4|e|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [0.041666667, 1E-8], 1: [-0.020833333, 1E-8],
                                                                2: [0.026872253, 1E-8], 3: [-0.013436126, 1E-8],
                                                                4: [0.010380483, 1E-8], 5: [-0.0051902415, 1E-8],
                                                                6: [0.0032098552, 1E-8], 7: [-0.0016049276, 1E-8],
                                                                8: [0.00089015921, 1E-8]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('e12|e3|e4|e5|e5|e|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [-0.016666667, 1E-8], 1: [0.0, 0.0],
                                                                2: [-0.0065822344, 1E-8], 3: [0.0, 0.0],
                                                                4: [-0.0014649679, 1E-8], 5: [0.0, 0.0],
                                                                6: [-0.00024589376, 1E-8], 7: [0.0, 0.0],
                                                                8: [-0.000035078170, 1E-8]}))

    diagram_calculator.set_expansion(g=graphine.Graph.fromStr('ee12|ee2|ee|'),
                                     rprime=r,
                                     momentum_derivative=False,
                                     e=numcalc.NumEpsExpansion({0: [0.25, 1E-8], 1: [-0.25, 1E-8],
                                                                2: [0.411234, 1E-8], 3: [-0.411234, 1E-8],
                                                                4: [0.473516, 1E-8], 5: [-0.473516, 1E-8],
                                                                6: [0.492776, 1E-8], 7: [-0.492776, 1E-8],
                                                                8: [0.498117, 1E-8]}))