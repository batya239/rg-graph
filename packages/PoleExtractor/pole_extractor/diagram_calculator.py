__author__ = 'gleb'

import pickle
import os
import datetime

import graphine

import reduced_vl
import numcalc
import feynman
import rprime
import utils


def gen_filename(g, rprime, momentum_derivative):
    """
    """
    assert(isinstance(g, (graphine.Graph, str)))

    fn = os.path.expanduser("~") + '/.pole_extractor/'
    if rprime:
        fn += 'RPRIME/'
    else:
        fn += 'BASE/'

    if isinstance(g, graphine.Graph):
        fn += str(g)[:-2]
    elif isinstance(g, str):
        fn += g
    if momentum_derivative:
        fn += 'p2'
    return fn


def is_present(g, rprime, momentum_derivative):
    return os.path.isfile(gen_filename(g, rprime, momentum_derivative))


def get_expansion(g, rprime, momentum_derivative):
    f = open(gen_filename(g, rprime, momentum_derivative), 'rb')
    result = pickle.load(f)
    f.close()
    return result


def set_expansion(g, rprime, momentum_derivative, e):
    f = open(gen_filename(g, rprime, momentum_derivative), 'wb')
    pickle.dump(e, f)
    f.close()


def clear(g, rprime, momentum_derivative):
    fname = gen_filename(g, rprime, momentum_derivative)
    if os.path.isfile(fname):
        os.remove(fname)


def update_expansion(g, rprime, momentum_derivative, e, force_update=False):
    if (not os.path.isfile(gen_filename(g, rprime, momentum_derivative))) or force_update:
        set_expansion(g, rprime, momentum_derivative, e)
    else:
        set_expansion(g, rprime, momentum_derivative,
                      numcalc.NumEpsExpansion.unite(get_expansion(g, rprime, momentum_derivative), e))


def term_factor_expansion(tf):
    if not isinstance(tf, rprime.RPrimeTermFactor):
        raise TypeError
    if not os.path.isfile(gen_filename(tf._diagram, rprime=tf._rprime, momentum_derivative=tf._derivative)):
        raise EnvironmentError('Diagram ' + str(tf) + ' is not yet calculated')

    e = get_expansion(tf._diagram, rprime=tf._rprime, momentum_derivative=tf._derivative)
    if tf._k:
        return e.cut(0)
    else:
        return e


def calculate_diagram(label, theory, max_eps, zero_momenta=True, force_update=False, adaptive=True):
    """
    """
    if isinstance(label, str):
        g = graphine.Graph.fromStr(label)
    elif isinstance(label, graphine.Graph):
        g = label
    else:
        raise TypeError('param :label: should be str or graphine.Graph')

    verbose = True
    log = True
    update = True

    begin = datetime.datetime.now()

    if log:
        utils.dispatch_log_message('\n\n\n', ts=False)
        utils.dispatch_log_message('Starting to calculate diagram ' + str(g))
    if verbose:
        print 'Graph:\n' + str(g)

    rvl = reduced_vl.ReducedVacuumLoop.fromGraphineGraph(g, zero_momenta=zero_momenta)
    gamma_coef = numcalc.NumEpsExpansion.gammaCoefficient(rvl, theory=theory, max_index=10)

    to_index = max_eps - min(gamma_coef.keys())

    fi = feynman.FeynmanIntegrand.fromRVL(rvl, theory)

    if log:
        utils.dispatch_log_message('Integrand:\n' + str(fi))
    if verbose:
        print 'Integrand:\n' + str(fi)

    ns = reduced_vl.all_SD_sectors(rvl)
    ss = reduced_vl.reduce_symmetrical_sectors(ns, g)
    if log:
        utils.dispatch_log_message('Non-symmetrical sectors (' + str(len(ss)) + '):\n' +
                                   '\n'.join(map(lambda x: str(x[0]) + ' * ' + str(x[1]), ss)))
    if verbose:
        print 'All sectors: ' + str(len(ns)) + '\nNon-symmetrical sectors: ' + str(len(ss))

    num_expansion = numcalc.NumEpsExpansion({k: [0.0, 0.0] for k in range(to_index + 1)}, precise=True)

    for i, sec in enumerate(ss):
        sec_expr = fi.sector_decomposition(sec)

        expansion = feynman.extract_poles(sec_expr._integrand, to_index + 1 + rvl.loops())
        expansion = {k: expansion[k] for k in expansion.keys() if k <= to_index}
        sector_n_expansion = numcalc.cuba_calculate(expansion, parallel_processes=2,
                                                    header_size=200, adaptive=adaptive)

        num_expansion += sector_n_expansion
        if log:
            utils.dispatch_log_message('\nCalculated sector:\n' + str(sec[0]) + ' * ' + str(sec[1]))
            utils.dispatch_log_message('With integrand:\n' + str(sec_expr), ts=False)
            utils.dispatch_log_message('With expansion length: ' +
                                       str(sum([len(expansion[k]) for k in expansion.keys()])), ts=False)
            utils.dispatch_log_message('With result:\n' + str(sector_n_expansion), ts=False)
        if verbose:
            print '\rCalculated: ' + str(i + 1) + '   ',

    result = num_expansion * gamma_coef

    if update:
        update_expansion(g, rprime=False, momentum_derivative=not zero_momenta, e=result, force_update=force_update)

    delta = datetime.datetime.now() - begin
    time_msg = 'Overall time:\n'
    hours = int(delta.seconds) / 3600
    minutes = (int(delta.seconds) % 3600) / 60
    seconds = (int(delta.seconds) % 3600) % 60
    for num, name in zip((hours, minutes, seconds), (' hour ', ' minute ', ' second ')):
        if num > 0:
            time_msg += str(num) + name
            if num > 1:
                time_msg = time_msg[:-1] + 's '

    if log:
        utils.dispatch_log_message(time_msg)

    if verbose:
        print '\nAll done!\n' + str(result)
        print time_msg + '\n'

    return result


def calculate_rprime(label, theory, verbose=1, force_update=False):
    """
    """
    def term_to_expansion(counter_term):
        get_expansions = map(lambda x: (float(x[0]), map(lambda y: term_factor_expansion(y), x[1])), counter_term)
        mul_expansions = map(lambda x: reduce(lambda y, z: y * z, x[1]) * x[0], get_expansions)
        return reduce(lambda x, y: x + y, mul_expansions)

    if isinstance(label, str):
        g = graphine.Graph.fromStr(label)
    elif isinstance(label, graphine.Graph):
        g = label
    exclusion_groups = rprime.shrinking_groups(g, theory)
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

    c_part = rprime.gen_cts(g, exclusion_groups, theory)
    if verbose > 1:
        print "Tau-counterterms:\n" + str(c_part)

    c_part_exp = term_to_expansion(c_part)
    if verbose > 1:
        print "Tau-counterterms calculated:\n" + str(c_part_exp)

    result = get_expansion(g, rprime=False, momentum_derivative=False) + c_part_exp
    if verbose > 0:
        print "R' tau-part:\n" + str(result)

    update_expansion(g, rprime=True, momentum_derivative=False, e=result, force_update=force_update)

    if 2 == g.externalEdgesCount():
        p2_part = rprime.gen_cts(g, exclusion_groups, theory, momentum_derivative=True)
        if verbose > 1:
            print "p^2-counterterms:\n" + str(p2_part)

        p2_part_exp = term_to_expansion(p2_part)
        if verbose > 1:
            print "p^2-counterterms calculated:\n" + str(p2_part_exp)

        result = get_expansion(g, rprime=False, momentum_derivative=True) + p2_part_exp
        if verbose > 0:
            print "R' p^2-part:\n" + str(result)

        update_expansion(g, rprime=True, momentum_derivative=True, e=result, force_update=force_update)
