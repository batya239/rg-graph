__author__ = 'gleb'

import pole_extractor.diagram_calculator

two_loops = ('e12-e3-33--', 'e12-23-3-e-', 'e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-')
test_labels = ('e111-e-', 'ee11-22-ee-', 'ee12-e22-e-',
               'e112-22-e-', 'ee11-22-33-ee-', 'ee11-23-e33-e-',
               'ee12-ee3-333--', 'ee12-e33-e33--', 'e112-e3-e33-e-',
               'ee12-e23-33-e-', 'e123-e23-e3-e-', 'ee12-223-3-ee-')
for l in two_loops:
    pole_extractor.diagram_calculator.calculate_rprime(l, PHI_EXPONENT=3, force_update=True, verbose=5)
    print
