__author__ = 'gleb'

import graphine
import pole_extractor.feynman as feynman
import pole_extractor.expansion
import pole_extractor.numcalc

"""
labels = ('e111-e-', 'ee11-22-ee-', 'ee12-e22-e-',
          'e112-22-e-', 'ee11-22-33-ee-', 'ee11-23-e33-e-',
          'ee12-ee3-333--', 'ee12-e33-e33--', 'e112-e3-e33-e-',
          'ee12-e23-33-e-', 'e123-e23-e3-e-', 'ee12-223-3-ee-')
labels = ('e12-e3-44-56-7-68-8-e8--',)
"""

labels2tails = ('111--', 'e12-e3-33--', 'e12-23-3-e-')
labels3tails = ('111--', 'e12-e3-e4-44--', 'e12-e3-34-4-e-', 'e12-34-34-e-e-')


def calc_expansion(label):
    g = graphine.Graph.fromStr(label)
    f = feynman.Feynman(g, theory=3)
    print '### ' + label + ':\n' + str(f)

    sectors = feynman.sectors(g, conservation_laws=f._conslaws, symmetries=True)
    #print "Symmetrically non-equivalent sectors: " + str(len(sectors))

    decomposed = map(lambda x: f.sector_decomposition(x), sectors)
    #for x in zip(sectors, decomposed):
    #    print str(x[0]) + ':\n' + str(x[1])

    expansions = map(lambda x: pole_extractor.expansion.extract_poles(x._integrand, 5), decomposed)

    num_expansion = pole_extractor.numcalc.NumEpsExpansion()
    i = 0
    for e in expansions:
        i += 1
        print '\rcalculating ' + str(i) + ' sector of ' + str(len(expansions)) + '...',
        num_expansion += pole_extractor.numcalc.CUBA_calculate(e)
        print ' done!',
    #print '\n' + str(num_expansion)
    g_coef = pole_extractor.numcalc.get_gamma(f._gamma_coef2[0], f._gamma_coef2[1], 5)
    g_coef = g_coef ** (f._gamma_coef2[2])
    g_coef *= pole_extractor.numcalc.get_gamma(f._gamma_coef1[0], f._gamma_coef1[1], 5)
    g_coef *= float(f._inverse_coefficient) ** (-1)
    result = g_coef * num_expansion
    #print "result: " + str(result)
    #print
    return result

print calc_expansion('e12-23-3-e-')