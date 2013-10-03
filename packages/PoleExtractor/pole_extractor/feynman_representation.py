__author__ = 'gleb'

import copy
import itertools
import polynomial
import nickel
import _conserv as conserv


def unique(seq):
    seen = set()
    return [x for x in seq if str(x) not in seen and not seen.add(str(x))]


class FeynmanRepresentation:
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
        Numerator = polynomial.poly(self._setup_numerator(edges_number))
        self._integrand = Denominator * Numerator
        self._delta_argument = polynomial.poly(self._setup_delta_argument(nick.edges))
        if momentum_derivative:
            c = polynomial.poly(self._setup_c(nick.edges, loops_number),
                                degree=(-edges_number + 2 + loops_number * deg, -loops_number)).set0toVar(edges_number)
            self._integrand = self._integrand * c.toPolyProd()
        self._gamma_coefs = []
        self._gamma_coefs.append((edges_number - tails_number - deg * loops_number, loops_number))
        self._gamma_coefs.append((deg, -1))

    def _setup_conslaws(self, edges):
        vacuum_loop = dict((n, e) for n, e in enumerate(edges) if -1 not in e)
        result = sorted([sorted(list(law)) for law in list(conserv.Conservations(vacuum_loop))])
        return tuple(map(lambda x: tuple(x), result))

    def _setup_determinant(self, edges, loops):
        det_base = filter(lambda x: -1 not in edges[x], range(0, len(edges)))
        det = unique(map(lambda x: sorted(x), list(itertools.permutations(det_base, loops))))
        for law in filter(lambda x: len(x) == 2, self._conslaws):
            for i, monomial in enumerate(det):
                det[i] = [law[1] if x == law[0] else x for x in monomial]
        det = unique(filter(lambda x: len(x) >= loops, map(lambda y: sorted(unique(y)), det)))
        det = filter(lambda x: all(map(lambda y: not set(y).issubset(x), self._conslaws)), det)
        return map(lambda x: (1, x), det)

    def _setup_numerator(self, edges_number):
        num_base = list(xrange(0, edges_number))
        for law in filter(lambda x: len(x) == 2, self._conslaws):
            num_base = [law[1] if x == law[0] else x for x in num_base]
        for edge in range(0, edges_number):
            if edge in num_base:
                num_base.remove(edge)
        return [(1, num_base), ]

    def _setup_c(self, edges, loops_number):
        new_edge = []
        for edge in edges:
            if -1 in edge[0:2]:
                new_edge += edge[0:2]
        new_edge = filter(lambda x: x != -1, new_edge)
        diag_for_c = copy.deepcopy(edges)
        diag_for_c.append(new_edge)
        c_base = self._setup_determinant(diag_for_c, loops_number + 1)
        return c_base

    def _setup_delta_argument(self, edges):
        base = filter(lambda x: -1 not in edges[x], range(0, len(edges)))
        for law in filter(lambda x: len(x) == 2, self._conslaws):
            base = filter(lambda x: law[0] != x, base)
        return map(lambda x: (1, [x, ]), base)

    def __str__(self):
        result = '||'
        for g in self._gamma_coefs:
            result += str(g[0]) + '+(' + str(g[1]) + '*eps)||'
        result += str(self._integrand) + '*DELTA[1-' + str(self._delta_argument) + "]"
        return result