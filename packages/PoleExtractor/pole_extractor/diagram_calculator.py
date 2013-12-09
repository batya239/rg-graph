__author__ = 'gleb'

import pickle
import os

import graphine
from graphine import filters
import graph_state

import reduced_vl
import numcalc
import feynman
import sector_decomposition
import expansion


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


class RPrimeTermFactor:
    """
    It's a class for storing additional info about diagrams while performing R':
    whether it should be or not derived by p^2,
    whether K must or not be performed over it.
    """
    DerivativePrefix = '{d/dp^2}'

    def __init__(self, diagram, k=False, derivative=False):
        assert(isinstance(diagram, graphine.Graph))
        self._diagram = diagram
        self._k = k
        self._derivative = derivative

    def diagram(self):
        return self._diagram

    def __str__(self):
        s = str()
        if self._derivative:
            s += RPrimeTermFactor.DerivativePrefix
        s += str(self._diagram)
        if self._k:
            s = '(' + s + ')'
        return s

    def __repr__(self):
        return str(self)

    @staticmethod
    def fromString(s):
        k_operation = False
        d = False
        if s[0] == '(' and s[-1] == ')':
            s = s[1:-1]
            k_operation = True
        if s[0:len(RPrimeTermFactor.DerivativePrefix)] == RPrimeTermFactor.DerivativePrefix:
            s = s[len(RPrimeTermFactor.DerivativePrefix):]
            d = True
        g = graphine.Graph.fromStr(s)
        return RPrimeTermFactor(g, k_operation, d)

    def get_expansion(self):
        assert(os.path.isfile(gen_filename(self._diagram, rprime=True, momentum_derivative=self._derivative)))
        e = get_expansion(self._diagram, rprime=True, momentum_derivative=self._derivative)
        if self._k:
            return e.cut(-1)
        else:
            return e


def r_prime_counterterms(label, PHI_EXPONENT, verbose=1, force_update=False):
    """
    """

    def intersect(graph1, graph2):
        return bool(graph1.vertices().difference({graph1.externalVertex, }).
                    intersection(graph2.vertices().difference({graph2.externalVertex, })))

    def update_groupings(group, subgraphs):
        result = []
        for i, sg in enumerate(subgraphs[group[0]:]):
            if not any(map(lambda x: intersect(x, sg), group[1])):
                result.append((i + group[0], group[1] + tuple([sg])))
        return result

    def add_adjoining_edge(sg, g):
        border_vertices = filter(lambda x: not x == sg.externalVertex,
                                 sum([list(e.nodes) for e in sg.externalEdges()], []))
        border_edges = filter(lambda x: x not in sg.allEdges(),
                              sum([g.edges(v) for v in border_vertices], []))
        return graphine.Graph(sg.allEdges() + [border_edges[0]], renumbering=False)

    def exclude_sg(term, sg):
        if 2 == sg.externalEdgesCount():
            sg2 = add_adjoining_edge(sg, term[1][-1])
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (-term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True), term[1][-1].shrinkToPoint(sg.internalEdges())]),
                    (term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True, derivative=True), term[1][-1].shrinkToPoint(sg2.internalEdges())])]
        else:
            return [(term[0], term[1][:-1] +
                    [RPrimeTermFactor(sg, k=True), term[1][-1].shrinkToPoint(sg.internalEdges())]), ]

    def update_tails(graph, exponent):
        vs = graph.vertices() - {graph.externalVertex}
        edges = []
        for v in vs:
            if len(graph.edges(v)) < exponent:
                edges += [graph_state.Edge((v, graph.externalVertex))] * (exponent - len(graph.edges(v)))
        return graphine.Graph(graph.allEdges() + edges)

    if 3 == PHI_EXPONENT:
        ext_count = (2, 3)
    elif 4 == PHI_EXPONENT:
        ext_count = (2, 4)
    else:
        return

    g = graphine.Graph.fromStr(label)
    sg_UV_filters = (filters.connected
                     + filters.oneIrreducible
                     + filters.noTadpoles)

    subgraphsUV = filter(lambda x: x.externalEdgesCount() in ext_count,
                         [subg for subg in g.xRelevantSubGraphs(filters=sg_UV_filters,
                                                                resultRepresentator=graphine.Representator.asGraph,
                                                                cutEdgesToExternal=True)])

    groupings = [(i, tuple([subgraphsUV[i]])) for i in range(len(subgraphsUV))]
    for group in groupings:
        groupings.extend(update_groupings(group, subgraphsUV))
    exclusion_groups = map(lambda x: x[1], groupings)

    result = []
    for group in exclusion_groups:
        counterterms = [(-1, [g, ]), ]
        for subgraph in group:
            counterterms = sum(map(lambda x: exclude_sg(x, subgraph), counterterms), [])
        for ctm in counterterms:
            ctm[1][-1] = update_tails(ctm[1][-1], PHI_EXPONENT)
            result.append((ctm[0], ctm[1][:-1] + [RPrimeTermFactor(ctm[1][-1])]))
            if 2 == ctm[1][-1].externalEdgesCount():
                result.append((ctm[0], ctm[1][:-1] + [RPrimeTermFactor(ctm[1][-1], derivative=True), 'p^2']))
    if verbose > 0:
        print 'Diagram: ' + str(g) + '\nCounterterms: ' + str(result)

    if 0 == len(result):
        update_expansion(g,
                         rprime=True,
                         momentum_derivative=False,
                         e=get_expansion(g, rprime=False, momentum_derivative=False))
        return get_expansion(g, rprime=False, momentum_derivative=False)

    c_part = filter(lambda x: 'p^2' not in x[1], result)
    exp_poly_c = map(lambda x: (x[0], map(lambda y: y.get_expansion(), x[1])), c_part)

    exp_c = reduce(lambda a, b: a + b, map(lambda x: reduce(lambda y, z: y * z, x[1]) * float(x[0]), exp_poly_c))
    if verbose > 1:
        print 'Tau-part: ' + str(c_part)
    if 2 == g.externalEdgesCount():
        p2_part = filter(lambda y: y is not None, map(lambda x: (x[0], x[1][:-1]) if 'p^2' in x[1] else None, result))
        exp_poly_p2 = map(lambda x: (x[0], map(lambda y: y.get_expansion(), x[1])), p2_part)
        exp_p2 = reduce(lambda a, b: a + b, map(lambda x: reduce(lambda y, z: y * z, x[1]) * float(x[0]), exp_poly_p2))

        if verbose > 1:
            print 'p^2-part: ' + str(p2_part)

        rpr_exp = (get_expansion(g, rprime=False, momentum_derivative=False) + exp_c,
                   get_expansion(g, rprime=False, momentum_derivative=True) + exp_p2)
        if verbose > 0:
            print 'Tau-part: ' + str(rpr_exp[0])
            print 'p^2-part: ' + str(rpr_exp[1])
        update_expansion(g, rprime=True, momentum_derivative=False, e=rpr_exp[0], force_update=force_update)
        update_expansion(g, rprime=True, momentum_derivative=True, e=rpr_exp[1], force_update=force_update)
        return rpr_exp
    else:
        rpr_exp = get_expansion(g, rprime=False, momentum_derivative=False) + exp_c
        if verbose > 0:
            print 'Tau-part: ' + str(rpr_exp)
        update_expansion(g, rprime=True, momentum_derivative=False, e=rpr_exp, force_update=force_update)
        return rpr_exp


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

    num_expansion = numcalc.NumEpsExpansion()
    i = 0
    for e in expansions:
        if verbose > 0:
            i += 1
            print '\rcalculating ' + str(i) + ' sector of ' + str(len(expansions)) + '...',
        num_expansion += numcalc.cuba_calculate(e[1])
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

    update_expansion(g, False, momentum_derivative=not zero_momenta, e=result, force_update=force_update)

    return result
