__author__ = 'gleb'

import pickle
import os

import graphine

import reduced_vl
import numcalc
import feynman
import sector_decomposition
import expansion
import rprime


def gen_filename(g, rprime, momentum_derivative):
    wd = os.path.expanduser("~") + '/.pole_extractor/'
    if rprime:
        wd += 'RPRIME/'
    else:
        wd += 'BASE/'
    fn = wd
    if isinstance(g, graphine.Graph):
        fn += str(g)[:-2]
    elif isinstance(g, str):
        fn += g
    if momentum_derivative:
        fn += 'p2'
    return fn


def get_expansion(g, rprime, momentum_derivative):
    f = open(gen_filename(g, rprime, momentum_derivative), 'rb')
    result = pickle.load(f)
    f.close()
    return result


def set_expansion(g, rprime, momentum_derivative, e):
    f = open(gen_filename(g, rprime, momentum_derivative), 'wb')
    pickle.dump(e, f)
    f.close()


def update_expansion(g, rprime, momentum_derivative, e, force_update=False):
    if (not os.path.isfile(gen_filename(g, rprime, momentum_derivative))) or force_update:
        set_expansion(g, rprime, momentum_derivative, e)
    else:
        set_expansion(g, rprime, momentum_derivative,
                      numcalc.NumEpsExpansion.unite(get_expansion(g, rprime, momentum_derivative), e))


def term_factor_expansion(tf):
    assert(isinstance(tf, rprime.RPrimeTermFactor))
    assert(os.path.isfile(gen_filename(tf._diagram, rprime=True, momentum_derivative=tf._derivative)))
    e = get_expansion(tf._diagram, rprime=True, momentum_derivative=tf._derivative)
    if tf._k:
        return e.cut(0)
    else:
        return e


def calculate_rprime(label, PHI_EXPONENT, verbose=1, force_update=False):
    """
    """
    def term_to_expansion(counter_term):
        get_expansions = map(lambda x: (float(x[0]), map(lambda y: term_factor_expansion(y), x[1])), counter_term)
        mul_expansions = map(lambda x: reduce(lambda y, z: y * z, x[1]) * x[0], get_expansions)
        return reduce(lambda x, y: x + y, mul_expansions)

    g = graphine.Graph.fromStr(label)
    exclusion_groups = rprime.shrinking_groups(g, PHI_EXPONENT)
    if len(exclusion_groups) == 0:
        update_expansion(g, rprime=True,
                         momentum_derivative=False,
                         e=get_expansion(g, rprime=False, momentum_derivative=False),
                         force_update=force_update)
        if 2 == g.externalEdgesCount():
            update_expansion(g, rprime=True,
                             momentum_derivative=True,
                             e=get_expansion(g, rprime=False, momentum_derivative=True),
                             force_update=force_update)
        return
    if verbose > 0:
        print "Graph: " + str(g)
    if verbose > 1:
        print "Non-overlapping subgraph groupings:\n" + str(exclusion_groups)

    #c_part = rprime.generate_counterterms(g, exclusion_groups, PHI_EXPONENT)
    c_part = rprime.gen_cts(g, exclusion_groups, PHI_EXPONENT)
    if verbose > 1:
        print "Tau-counterterms:\n" + str(c_part)

    c_part_exp = -1 * term_to_expansion(c_part)
    if verbose > 1:
        print "Tau-counterterms calculated:\n" + str(c_part_exp)

    result = get_expansion(g, rprime=False, momentum_derivative=False) + c_part_exp
    if verbose > 0:
        print "R' tau-part:\n" + str(result)

    update_expansion(g, rprime=True, momentum_derivative=False, e=result, force_update=force_update)

    if 2 == g.externalEdgesCount():
        #p2_part = rprime.generate_counterterms(g, exclusion_groups, PHI_EXPONENT, momentum_derivative=True)
        p2_part = rprime.gen_cts(g, exclusion_groups, PHI_EXPONENT, momentum_derivative=True)
        if verbose > 1:
            print "p^2-counterterms:\n" + str(p2_part)

        p2_part_exp = -1 * term_to_expansion(p2_part)
        if verbose > 1:
            print "p^2-counterterms calculated:\n" + str(p2_part_exp)

        result = get_expansion(g, rprime=False, momentum_derivative=True) + p2_part_exp
        if verbose > 0:
            print "R' p^2-part:\n" + str(result)

        update_expansion(g, rprime=True, momentum_derivative=True, e=result, force_update=force_update)


def calculate_diagram(label, theory, max_eps, zero_momenta=True, verbose=1, force_update=False):
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

    num_expansion = numcalc.NumEpsExpansion({k: [0.0, 0.0] for k in range(max_eps + 1)}, precise=True)
    i = 0
    for e, s in zip(expansions, ss):
        if 1 >= verbose > 0:
            i += 1
            print '\rcalculating ' + str(i) + ' sector of ' + str(len(expansions)) + '...',

        sector_expansion = numcalc.cuba_calculate(e[1])
        num_expansion += sector_expansion

        if 1 >= verbose > 0:
            print ' done!',
        elif verbose > 1:
            print 'Sector: ' + str(s[0]) + ' * ' + str(s[1]) + '\nExpansion:\n' + str(sector_expansion)
    if 1 >= verbose > 0:
        print "\rResult of numerical integration:\n" + str(num_expansion)
    elif verbose > 1:
        print "Result of numerical integration:\n" + str(num_expansion)

    gamma_coef = numcalc.NumEpsExpansion.gammaCoefficient(rvl,
                                                          theory=theory,
                                                          max_index=max_eps)
    result = num_expansion * gamma_coef

    if verbose > 0:
        print "Result multiplied by Gammas:\n" + str(result)

    update_expansion(g, False, momentum_derivative=not zero_momenta, e=result, force_update=force_update)

    return result