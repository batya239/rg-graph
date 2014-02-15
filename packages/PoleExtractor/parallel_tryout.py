__author__ = 'gleb'

import graphine

from pole_extractor import reduced_vl
from pole_extractor import numcalc
from pole_extractor import feynman
from pole_extractor import sector_decomposition
from pole_extractor import expansion
from pole_extractor import utils


def calculate_diagram(label, theory, max_eps, zero_momenta=True, verbose=1):
    if isinstance(label, str):
        g = graphine.Graph.fromStr(label)
    elif isinstance(label, graphine.Graph):
        g = label

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
    if verbose > 3:
        for s in ns:
            print str(s[1])

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

    for e, s in zip(expansions, ss):
        sector_expansion1 = numcalc.cuba_calculate(e[1])
        sector_expansion2 = numcalc.parallel_cuba_calculate(e[1])

        print '### ' + str(sector_expansion1)
        print '### ' + str(sector_expansion2)


need_p2 = utils.get_diagrams(tails=2, loops=2)
need_p0 = need_p2 + utils.get_diagrams(tails=3, loops=2)

for diag in need_p0:
    calculate_diagram(label=diag[0], theory=3, max_eps=4, zero_momenta=True, verbose=2)

for diag in need_p2:
    calculate_diagram(label=diag[0], theory=3, max_eps=4, zero_momenta=False, verbose=2)