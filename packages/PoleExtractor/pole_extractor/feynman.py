__author__ = 'gleb'

import itertools
import polynomial
import math
import copy
import reduced_vl


class FeynmanIntegrand:
    def __init__(self, integrand, delta_argument):
        self._integrand = integrand
        self._delta_argument = delta_argument

    def __str__(self):
        if self._delta_argument:
            result = '*DELTA[1-' + str(self._delta_argument) + ']'
        else:
            result = ''
        return str(self._integrand) + result

    def __repr__(self):
        return str(self)

    @staticmethod
    def determinant(variables, loops, conservation_laws):
        det = list(set(map(lambda x: tuple(sorted(x)), list(itertools.permutations(variables, loops)))))
        det = filter(lambda x: all(map(lambda y: not set(y).issubset(x), conservation_laws)), det)
        return map(lambda x: (1, list(x)), det)

    @staticmethod
    def fromRVL(rvl, theory):
        """
        Calculates integrand of Feynman's interpretation if rvl is on zero momenta,
        and d/dp^2 of integrand if rvl is not.
        """
        #TODO: checking btw p=0 & d/dp^2 should probably be done somewhat different
        assert (isinstance(rvl, reduced_vl.ReducedVacuumLoop))
        assert (theory in (3, 4))

        deg = 0 - int(not rvl.zero_momenta())
        if 3 == theory:
            deg -= 3
        elif 4 == theory:
            deg -= 2

        loops = rvl.loops()
        edges = rvl.edges()
        cons_laws = rvl.conservation_laws(exclude_ext_edges=True)

        coef = reduce(lambda x, y: x * y, map(lambda z: math.factorial(z - 1), rvl.edges_weights()))
        integrand = polynomial.poly([(1, sum(map(lambda x: [x[0]] * (x[1] - 1), rvl.edges_with_weights()), []))],
                                    c=(coef**(-1) * 2**(-loops)))

        integrand *= polynomial.poly(FeynmanIntegrand.determinant(edges, loops, cons_laws), degree=(deg, 1))
        d_arg = polynomial.poly(map(lambda x: (1, [x]), edges))

        if not rvl.zero_momenta():
            laws_for_c = rvl.internal_conservation_laws()
            integrand *= polynomial.poly(FeynmanIntegrand.determinant(edges, loops + 1, laws_for_c))

        return FeynmanIntegrand(integrand, d_arg)

    def sector_decomposition(self, sector):
        result = copy.deepcopy(self)
        res = polynomial.sd_lib.sectorDiagram(result._integrand, sector[1], result._delta_argument)[0][0]
        coefficient = polynomial.poly([(1, []), ], degree=1, c=sector[0])
        res *= coefficient.toPolyProd()
        result._delta_argument = None
        result._integrand = res.simplify()
        return result