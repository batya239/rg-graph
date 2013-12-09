__author__ = 'gleb'

import pole_extractor.diagram_calculator

two_loops = ('e12-e3-33--', 'e12-23-3-e-', 'e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-')
for l in two_loops:
    pole_extractor.diagram_calculator.calculate_rprime(l, 3, force_update=True, verbose=5)
    print
