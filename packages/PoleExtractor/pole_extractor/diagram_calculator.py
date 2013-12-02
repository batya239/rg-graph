__author__ = 'gleb'

import graphine
import reduced_vl
import numcalc
import feynman
import sector_decomposition
import expansion


def calculate_diagram(label, theory, max_eps, zero_momenta=True, verbose=1):
    g = graphine.Graph.fromStr(label)
    if verbose > 0:
        print "Graph: " + str(g)

    rvl = reduced_vl.ReducedVacuumLoop.fromGraphineGraph(g, zero_momenta=zero_momenta)
    if verbose > 1:
        print "Reduced v-loop: " + str(rvl)

    fi = feynman.FeynmanIntegrand.fromRVL(rvl, theory)
    if verbose > 0:
        print "Feynman integrand:\n" + str(fi)

    ns = sector_decomposition.sectors(rvl)
    if verbose > 1:
        print "SD Sectors: " + str(len(ns))

    ss = sector_decomposition.reduce_symmetrical_sectors(ns, g)
    if verbose > 0:
        print "Non-symmetric SD Sectors: " + str(len(ss))
    if verbose > 2:
        for s in ss:
            print str(s[0]) + " * " + str(s[1])

    sector_expressions = map(lambda x: (x, fi.sector_decomposition(x)), ss)
    if verbose > 1:
        print "Decomposed integrand:"
        for s in sector_expressions:
            print "{" + str(s[0][0]) + " * " + str(s[0][1]) + "}->\n" + str(s[1])

    expansions = map(lambda x: (x[0], expansion.extract_poles(x[1]._integrand, max_eps)), sector_expressions)
    if verbose > 2:
        print "Analytical continuations:"
        for s in expansions:
            print "{" + str(s[0][0]) + " * " + str(s[0][1]) + "}->"
            for k in sorted(s[1].keys()):
                print "eps^{" + str(k) + "}: " + str(s[1][k])

    num_expansion = numcalc.NumEpsExpansion()
    i = 0
    for e in expansions:
        if verbose > 0:
            i += 1
            print '\rcalculating ' + str(i) + ' sector of ' + str(len(expansions)) + '...',
        num_expansion += numcalc.CUBA_calculate(e[1])
        if verbose > 0:
            print ' done!',
    if verbose > 0:
        print "\rResult of numerical integration:\n" + str(num_expansion)

    gamma_coef = numcalc.NumEpsExpansion.gammaCoefficient(rvl,
                                                          theory=theory,
                                                          max_index=max_eps)
    result = num_expansion * gamma_coef
    if verbose > 0:
        print "Result multiplied by Gammas:\n" + str(result)

    return num_expansion * gamma_coef