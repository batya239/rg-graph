__author__ = 'gleb'

import nickel
import graphine
import pole_extractor.feynman as feynman


labels = ('e111-e-', 'ee11-22-ee-', 'ee12-e22-e-',
          'e112-22-e-', 'ee11-22-33-ee-', 'ee11-23-e33-e-',
          'ee12-ee3-333--', 'ee12-e33-e33--', 'e112-e3-e33-e-',
          'ee12-e23-33-e-', 'e123-e23-e3-e-', 'ee12-223-3-ee-')
"""
labels = ('e12-e3-44-56-7-68-8-e8--',)
"""
for label in labels:
    g = graphine.Graph.fromStr(label)
    f = feynman.Feynman(g, theory=3)
    print '### ' + label + ':\n' + str(f)

    sectors = feynman.sectors(g, conservation_laws=f._conslaws, symmetries=True)
    print "Symmetrically non-equivalent sectors: " + str(len(sectors))

    decomposed = map(lambda x: f.sector_decomposition(x), sectors)
    for x in zip(sectors, decomposed):
        print str(x[0]) + ':\n' + str(x[1])
    print