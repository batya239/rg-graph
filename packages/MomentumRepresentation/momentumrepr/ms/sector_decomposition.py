#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import collections
import feyn_repr
import graph_state
import itertools
import configure_mr
from rggraphutil import emptyListDict


DEBUG = True
VERIFY = True

SubstitutedSector = collections.namedtuple("SubstitutedSector", ["expression", "variable_substitutors"])


def strategy_a(node):
    # TODO
    # return
    d = node.d
    enumerated_indices = list(d.getVarsIndexes())
    corners = determine_corners(d, enumerated_indices)
    if len(corners) < 2:
        is_unit_exist = False
        simplified = d.toPolyProd().simplify()
        if len(simplified) == 1:
            assert len(simplified.getVarsIndexes()) == 1
            p = simplified.polynomials[0]
            assert len(p.monomials) == 1
            is_unit_exist = True
        else:
            for p in simplified.polynomials:
                for m in p.monomials.keys():
                    if not len(m.vars):
                        is_unit_exist = True
                        break
        assert is_unit_exist
        return
    decomposition_space = find_decomposition_set(corners)

    for primary in decomposition_space:
        secondary = decomposition_space - {primary}
        if configure_mr.Configure.debug():
            print "\t" * (len(node._previous_primaries) + 1) + "p: " + str(primary) + ", s: " + str(secondary)
        new_node = SectorNode(primary, secondary, node._previous_primaries + (primary, ), node.alpha_params)
        new_node.d = d.stretch(primary, [list(secondary)[0]])
        new_node.build_tree(strategy_a)
        node._children.append(new_node)


def determine_corners(determinant, enumeration_index):
    monomials = list(determinant.monomials)
    assert len(monomials)
    corners = list()

    def compare_monomials(m1, m2):
        for idx in enumeration_index:
            res = cmp(m1.getVarPower(idx, 0), m2.getVarPower(idx, 0))
            if res != 0:
                return res
        return 0

    def remove_subordinates(corner):
        monomials.remove(corner)
        for m in list(monomials):
            do_remove = True
            for idx in enumeration_index:
                res = cmp(corner.getVarPower(idx, 0), m.getVarPower(idx, 0))
                if res > 0:
                    do_remove = False
                    break
            if do_remove:
                monomials.remove(m)

    while len(monomials):
        min_monomial = None
        for m in monomials:
            if min_monomial is None:
                min_monomial = m
            elif compare_monomials(m, min_monomial) < 0:
                min_monomial = m

        corners.append(min_monomial)
        remove_subordinates(min_monomial)

    return corners


def find_decomposition_set(corners):
    assert len(corners) > 1, corners
    vectors = list()
    for m1, m2 in itertools.permutations(corners, 2):
        vector = m1.linearSubtraction(m2)
        vectors.append(vector)

    def l(_v):
        return max(_v.vars.values()) - min(_v.vars.values())

    def n(_v):
        return _v.vars.values().count(max(_v.vars.values())) + _v.vars.values().count(min(_v.vars.values()))

    vectors = sorted(vectors, key=lambda v: (l(v), n(v)))
    min_v = vectors[0]

    _max = max(min_v.vars.values())
    _min = min(min_v.vars.values())
    _max_u = None
    _min_u = None

    for v, p in min_v.vars.items():
        if _max_u is None and p == _max:
            _max_u = v
        if _min_u is None and p == _min:
            _min_u = v
        if _min_u is not None and _max_u is not None:
            break

    assert _max_u is not None
    assert _min_u is not None

    return {_max_u, _min_u}


def verify(sectors):
    for s in sectors:
        verify_sector(s[0])


def verify_sector(s):
    for m in s:
        if not len(m):
            return
    assert False, s


class SectorsTree(object):
    def __init__(self, graph, conversation_laws, d):
        self._children = list()
        self.graph = graph
        self.conversation_laws = conversation_laws
        self.d = d

    def build_tree(self, strategy):
        alpha_params = self.d.getVarsIndexes()
        primaries = filter(lambda p: "a" not in str(p), alpha_params)
        # primaries = alpha_params

        for primary in primaries:
            secondary = set(primaries) - {primary}
            if configure_mr.Configure.debug():
                print "p: " + str(primary) + ", s: " + str(secondary)
            node = SectorNode(primary, secondary, tuple(), alpha_params)
            node.graph = self.graph
            node.conversation_laws = self.conversation_laws
            node.d = self.d.stretch(primary, secondary)
            self._children.append(node)
            node.build_tree(strategy)

    def substitute(self, d):
        result = list()
        for n in self._children:
            n._substitute(d, emptyListDict(), result)
        return result

    def get_all_sectors(self):
        result = list()
        for n in self._children:
            n.get_all_sectors(result, tuple())
        return result


class SectorNode(object):
    def __init__(self, primary_index, secondary_indices, previous_primaries, alpha_params):
        self.primary_index = primary_index
        self.secondary_indices = secondary_indices
        self._previous_primaries = previous_primaries
        self.alpha_params = alpha_params

        self._children = list()

    def get_all_sectors(self, visitor, previous):
        current = previous + ((self.primary_index, self.secondary_indices), )
        if len(self._children):
            for n in self._children:
                n.get_all_sectors(visitor, current)
        else:
            visitor.append(current)

    def find_substitutors(self, substitutor, visitor):
        substitutor = dict(substitutor)
        for s in self.secondary_indices:
            substitutor[s].append(self.primary_index)
        if not(len(self._children)):
            visitor.append(substitutor)
        else:
            for n in self._children:
                n.find_substitutors(substitutor, visitor)

    def build_tree(self, strategy):
        strategy(self)

        # dec_space = set()
        # for p in self.alpha_params:
        #     if p != self.primary_index and p not in self._previous_primaries:
        #         conversation_law_to_check = set(self._previous_primaries) | {self.primary_index} | {p}
        #         is_suitable = True
        #         for law in self._conversation_laws:
        #             if law.issubset(conversation_law_to_check):
        #                 is_suitable = False
        #                 break
        #         if not is_suitable:
        #             continue
        #         dec_space.add(p)
        #
        # if len(dec_space) < 2:
        #     return
        #
        # for p in dec_space:
        #     new_secondaries = dec_space - {p}
        #     if DEBUG:
        #             print "\t" * (len(self._previous_primaries) + 1) + "p: " + str(p) + ", s: " + str(new_secondaries)
        #     node = SectorNode(p,
        #                       new_secondaries,
        #                       self._previous_primaries + (self.primary_index, ),
        #                       self._conversation_laws,
        #                       self.alpha_params)
        #     self._children.append(node)
        #     node.build_tree()

    def _substitute(self, d, substitutor, result):
        def stretch_monomial(monomial):
            new_monomial = list()
            for i in monomial:
                new_monomial.append(i)
                if i in self.secondary_indices:
                    new_monomial.append(self.primary_index)
            return new_monomial

        new_substitutor = emptyListDict()
        for k, v in substitutor.iteritems():
            new_substitutor[k] = list(v)
        substitutor = new_substitutor

        for s in self.secondary_indices:
            substitutor[s].append(self.primary_index)

        d = map(stretch_monomial, d)
        if len(self._children):
            for child in self._children:
                child._substitute(d, substitutor, result)
        else:
            powers = dict()
            is_first = True
            for m in d:
                for p in self.alpha_params:
                    c = m.count(p)
                    if is_first:
                        powers[p] = c
                    else:
                        if p in powers:
                            if c == 0:
                                del powers[p]
                            else:
                                powers[p] = min(powers[p], c)
                is_first = False

            def divide(monomial):
                for p, c in powers.iteritems():
                    for i in xrange(c):
                        monomial.remove(p)
            map(divide, d)
            result.append((d, powers, substitutor))


MAIN_GRAPH_CONFIG = graph_state.PropertiesConfig.create(graph_state.PropertyKey(name="fields",
                                                                                is_directed=True,
                                                                                externalizer=graph_state.Fields.externalizer()))

def calculate_sectors(strategy, _d, graph):
    conv_laws = set() #feyn_repr.determine_conservation_laws(graph)
    tree = SectorsTree(graph, conv_laws, _d)
    tree.build_tree(strategy)
    return tree