__author__ = 'gleb'

import graphine
import pole_extractor.feynman as feynman
import pole_extractor.expansion
import pole_extractor.numcalc


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

    expansions = map(lambda x: pole_extractor.expansion.extract_poles(x._integrand, 5), decomposed)

    num_expansion = dict()
    i = 0
    for e in expansions:
        i += 1
        print '\rcalculating ' + str(i) + ' sector of ' + str(len(expansions)) + '...',
        ne = pole_extractor.numcalc.compute_exp_via_CUBA(e)
        print ' done!',
        for k in ne.keys():
            if k not in num_expansion.keys():
                num_expansion[k] = [0.0, 0.0]
            num_expansion[k][0] += ne[k][0]
            num_expansion[k][1] += ne[k][1]
    print
    for k in sorted(num_expansion.keys()):
        print "eps^{" + str(k) + "}: " + str(num_expansion[k][0]) + "+-" + str(num_expansion[k][1])
    print

"""
diag_expansion = ec.NumEpsExpansion(numeric_expansion)
g1_expansion = ec.NumEpsExpansion(gamma.get_gamma(feynman_repr['gamma arguments'][0],
                                                  feynman_repr['gamma arguments'][1], max_eps))
g2_expansion = ec.NumEpsExpansion(gamma.get_gamma(feynman_repr['gamma arguments'][2],
                                                  feynman_repr['gamma arguments'][3], max_eps))
g2_coefficient = copy.deepcopy(g2_expansion)
for _ in itertools.repeat(None, g_info['loops'] - 1):
    g2_coefficient = g2_expansion * g2_coefficient

result_expansion = diag_expansion * g1_expansion * g2_coefficient
print 'Whole diagram with Gamma-function poles:'
for k in sorted(result_expansion.keys()):
    print 'eps^{' + str(k) + '}:'
    print str(result_expansion[k][0]) + " +- " + str(result_expansion[k][1])
    print
"""