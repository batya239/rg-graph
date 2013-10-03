__author__ = 'gleb'

import nickel
import pole_extractor.feynman_construction as feynman


labels = ('e111-e-', 'ee11-22-ee-', 'ee12-e22-e-',
          'e112-22-e-', 'ee11-22-33-ee-', 'ee11-23-e33-e-',
          'ee12-ee3-333--', 'ee12-e33-e33--', 'e112-e3-e33-e-',
          'ee12-e23-33-e-', 'e123-e23-e3-e-', 'ee12-223-3-ee-')

for label in labels:
    n = nickel.Nickel(string=label)
    f = feynman.Feynman(n, theory=4)
    print '### ' + label + ':\n' + str(f)
    if len(filter(lambda x: -1 in x, n.edges)) == 2:
        f2 = feynman.Feynman(n, momentum_derivative=True, theory=4)
        print f2
    print