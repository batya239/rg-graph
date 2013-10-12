__author__ = 'gleb'

import copy
import itertools
import polynomial
import math
import nickel
import _conserv as conserv
import graph_state
import polynomial.sd_lib as sd_lib


def unique(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]


def unite(seq):
    """
    turns sequence of sequences in sequence of elements of sequences, e.g.
    [[1, 2, 3], [4, 5], [6,]] -> [1, 2, 3, 4, 5, 6]
    """
    s = copy.deepcopy(seq)
    result = []
    while s:
        result.extend(s.pop(0))
    return result


def prepare_cons_laws(edges):
    """
    takes list of edges as returned by nickel.Nickel.edges
    returns immutable list of conservation laws
    """
    vacuum_loop = dict((n, e) for n, e in enumerate(edges) if -1 not in e)
    result = sorted([sorted(list(law)) for law in list(conserv.Conservations(vacuum_loop))])
    conservation_laws = tuple(map(lambda x: tuple(x), result))
    return conservation_laws


def prepare_edges(edges, conservation_laws):
    """
    returns list of numbers of internal edges repeated as many times as they are in diagram,
    e.g. result.count(result[i]) == \lambda_i in Feynman's representation
    """
    vl = list(range(len(edges)))
    vl = filter(lambda x: -1 not in edges[x], vl)

    for law in filter(lambda x: len(x) == 2, conservation_laws):
        vl = [law[1] if x == law[0] else x for x in vl]
    return vl


class Feynman:
    def __init__(self, nick, momentum_derivative=False, theory=0):
        if not isinstance(nick, nickel.Nickel):
            raise AttributeError('You are supposed to construct it from a nickel.Nickel instance')

        tails_number = len(filter(lambda x: -1 in x, nick.edges))
        if tails_number != 2 and momentum_derivative:
            raise AttributeError('Nope, it does not work that way')

        if theory == 3:
            deg = 3
        elif theory == 4:
            deg = 2
        else:
            raise AttributeError('Nope, it does not work that way. theory=3 for phi^3 and theory=4 for phi^4 diagrams.')

        self._conslaws = self._setup_conslaws(nick.edges)

        edges_number = len(nick.edges)
        vertices_number = len(nick.adjacent.keys())
        loops_number = edges_number - tails_number - vertices_number + 1

        Denominator = polynomial.poly(self._setup_determinant(nick.edges, loops_number), degree=(-deg, 1))
        _numerator = self._setup_numerator(nick.edges)
        Numerator = polynomial.poly(_numerator)
        self._integrand = Denominator * Numerator
        self._delta_argument = polynomial.poly(self._setup_delta_argument(nick.edges))
        if momentum_derivative:
            c = polynomial.poly(self._setup_c(nick.edges, loops_number),
                                degree=(-edges_number + 2 + loops_number * deg, -loops_number)).set0toVar(edges_number)
            self._integrand = self._integrand * c.toPolyProd()
        self._gamma_coef1 = (edges_number - tails_number - deg * loops_number, loops_number)
        self._gamma_coef2 = (deg, -1, loops_number)
        g = dict((i, _numerator[0][1].count(i)) for i in _numerator[0][1]).values()
        coef = 1
        for i in g:
            coef *= math.factorial(i)
        coef *= 2 ** loops_number
        self._inverse_coefficient = coef

    def _setup_conslaws(self, edges):
        return prepare_cons_laws(edges)

    def _setup_determinant(self, edges, loops, conslaws=None):
        if not conslaws:
            conslaws = self._conslaws
        det_base = filter(lambda x: -1 not in edges[x], range(0, len(edges)))
        det = unique(map(lambda x: sorted(x), list(itertools.permutations(det_base, loops))))
        for law in filter(lambda x: len(x) == 2, conslaws):
            for i, monomial in enumerate(det):
                det[i] = [law[1] if x == law[0] else x for x in monomial]
        det = unique(filter(lambda x: len(x) >= loops, map(lambda y: sorted(unique(y)), det)))
        det = filter(lambda x: all(map(lambda y: not set(y).issubset(x), conslaws)), det)
        return map(lambda x: (1, x), det)

    def _setup_numerator(self, edges):
        num_base = prepare_edges(edges, self._conslaws)

        for edge in range(0, len(edges)):
            if edge in num_base:
                num_base.remove(edge)
        return [(1, num_base), ]

    def _setup_c(self, edges, loops_number):
        diag_for_c = copy.deepcopy(edges)
        new_edge = filter(lambda x: x != -1, unite(filter(lambda x: -1 in x, edges)))
        diag_for_c.append(new_edge)
        conslaws_for_c = self._setup_conslaws(diag_for_c)
        c_base = self._setup_determinant(diag_for_c, loops_number + 1, conslaws=conslaws_for_c)
        return c_base

    def _setup_delta_argument(self, edges):
        base = filter(lambda x: -1 not in edges[x], range(0, len(edges)))
        for law in filter(lambda x: len(x) == 2, self._conslaws):
            base = filter(lambda x: law[0] != x, base)
        return map(lambda x: (1, [x, ]), base)

    def sector_decomposition(self, sector):
        result = copy.deepcopy(self)
        res = sd_lib.sectorDiagram(result._integrand, sector[1], result._delta_argument)[0][0]
        coefficient = polynomial.poly([(1, []), ], degree=1, c=sector[0] / float(result._inverse_coefficient))
        res *= coefficient.toPolyProd()
        res = res.simplify()
        result._delta_argument = None
        result._inverse_coefficient = None
        result._integrand = res
        return result

    def __str__(self):
        result = '(||'
        result += str(self._gamma_coef1[0]) + '+(' + str(self._gamma_coef1[1]) + '*eps)||'
        result += str(self._gamma_coef2[0]) + '+(' + str(self._gamma_coef2[1]) + '*eps)||^('
        result += str(self._gamma_coef2[2]) + ')'
        if self._inverse_coefficient:
            result += '/' + str(self._inverse_coefficient)
        result += ')' + str(self._integrand)
        if self._delta_argument:
            result += '*DELTA[1-' + str(self._delta_argument) + "]"
        return result


def sectors(nick, conservation_laws=None, symmetries=True):
    """
    returns sectors as tuple of elements (coef, sector), where
    coef is a symmetry coefficient, and
    sector is sector as ((main_variable_1, ()), (main_variable_1, ()), ...)
    """
    if not isinstance(nick, nickel.Nickel):
        raise AttributeError('Sectors must be generated from a nickel.Nickel instance')
    if not conservation_laws:
        conservation_laws = prepare_cons_laws(nick.edges)

    loops_number = len(nick.edges) - len(filter(lambda x: -1 in x, nick.edges)) - len(nick.adjacent.keys()) + 1
    variable_list = unique(prepare_edges(nick.edges, conservation_laws))

    dec_subspace = variable_list
    main_vars = tuple(itertools.permutations(dec_subspace, loops_number))
    result = []
    sector = []

    for p in main_vars:
        for edge in p:
            dec_subspace = tuple(x for x in dec_subspace if x != edge)
            sector.append((edge, dec_subspace))
        result.append(copy.copy(sector))
        del sector[:]
        dec_subspace = variable_list

    for law in filter(lambda x: len(x) > 2, conservation_laws):
        # removing sectors that have conservation laws in their main variables
        for i in reversed(range(len(result))):
            if set(map(lambda x: x[0], result[i])).issuperset(set(law)):
                result.pop(i)

        # removing sectors that are unnecessary after removing ones with conservation laws
        for sector in result:
            for i in range(2, len(sector)):
                main_vars = map(lambda x: x[0], sector[:i])
                if not len(set(law) - set(main_vars)) == 1:
                    continue
                for j in range(i, len(sector)):
                    if set(main_vars + list(sector[j][1])).issuperset(set(law)):
                        sector[j] = (sector[j][0], tuple(x for x in sector[j][1] if x not in law))

    for i in range(len(result)):
        result[i] = tuple(filter(lambda x: not len(x[1]) == 0, result[i]))

    if not symmetries:
        return tuple(map(lambda x: (1, x), result))

    sym_result = []

    d = copy.deepcopy(nick.edges)

    for edge in d:
        if len(edge) == 2:
            edge.append(0)

    test_diagrams = []
    for _ in itertools.repeat(None, len(result)):
        test_diagrams.append(copy.deepcopy(d))

    for sec_num, sector in enumerate(result):
        for dec_num, dec in enumerate(sector):
            test_diagrams[sec_num][dec[0]][2] = dec_num + 1

    labels = []
    for d in test_diagrams:
        labels.append(str(graph_state.GraphState(map(lambda x: graph_state.Edge(x[0:2], colors=x[2]), d))))

    for num, label in enumerate(labels):
        if not label in labels[0:num]:
            sym_result.append((labels.count(label), result[num]))

    return tuple(sym_result)