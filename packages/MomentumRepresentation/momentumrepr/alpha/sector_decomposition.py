#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import collections
import alpha_representation
import graph_state
import copy
from rggraphenv import symbolic_functions
from rggraphutil import emptyListDict


DEBUG = True
VERIFY = True

SubstitutedSector = collections.namedtuple("SubstitutedSector", ["expression", "variable_substitutors"])


def apply_sector_decomposition(graph, conversation_laws, d, use_symmetries=False, to_expr=False):
    u0 = alpha_representation.AlphaParameter.external()
    conversation_laws = map(lambda l: l - {u0}, conversation_laws)
    tree = sector_decomposition(graph, conversation_laws, use_symmetries)
    sectors = tree.substitute(d)
    if VERIFY:
        verify(sectors)
    if to_expr:
        sector_exprs = list()
        for s, multiplier, substitutor in sectors:
            expr = symbolic_functions.CLN_ZERO
            for m in s:
                expr += reduce(lambda x, i: x * i.as_var(), m, symbolic_functions.CLN_ONE)
            for p, c in multiplier.iteritems():
                expr *= p.as_var() ** c
            sector_exprs.append((expr, substitutor))
        return sector_exprs
    else:
        return sectors


def sector_decomposition(graph, conversation_laws, use_symmetries=False):
    assert not use_symmetries
    tree = SectorsTree(graph, conversation_laws)
    tree.build_tree()
    return tree


def verify(sectors):
    for s in sectors:
        verify_sector(s[0])


def verify_sector(s):
    for m in s:
        if not len(m):
            return
    assert False, s


class SectorsTree(object):
    def __init__(self, graph, conversation_laws):
        self._children = list()
        self._graph = graph
        self._conversation_laws = conversation_laws

        self._built = False

    def build_tree(self):
        alpha_params = set(map(lambda e: e.alpha_param, self._graph.internal_edges))
        for primary in alpha_params:
            secondary = alpha_params - {primary}
            if DEBUG:
                print "p: " + str(primary) + ", s: " + str(secondary)
            node = SectorNode(primary, secondary, tuple(), self._conversation_laws, alpha_params)
            self._children.append(node)
            node.build_tree()
        self._built = True

    def substitute(self, d):
        assert self._built
        result = list()
        for n in self._children:
            n._substitute(d, emptyListDict(), result)
        return result


class SectorNode(object):
    def __init__(self, primary_index, secondary_indices, previous_primaries, conversation_laws, alpha_params):
        self.primary_index = primary_index
        self.secondary_indices = secondary_indices
        self.alpha_params = alpha_params

        self._previous_primaries = previous_primaries
        self._conversation_laws = conversation_laws
        self._children = list()

    def build_tree(self):
        dec_space = set()
        for p in self.alpha_params:
            if p != self.primary_index and p not in self._previous_primaries:
                conversation_law_to_check = set(self._previous_primaries) | {self.primary_index} | {p}
                is_suitable = True
                for law in self._conversation_laws:
                    if law.issubset(conversation_law_to_check):
                        is_suitable = False
                        break
                if not is_suitable:
                    continue
                dec_space.add(p)

        if len(dec_space) < 2:
            return

        for p in dec_space:
            new_secondaries = dec_space - {p}
            if DEBUG:
                    print "\t" * (len(self._previous_primaries) + 1) + "p: " + str(p) + ", s: " + str(new_secondaries)
            node = SectorNode(p,
                              new_secondaries,
                              self._previous_primaries + (self.primary_index, ),
                              self._conversation_laws,
                              self.alpha_params)
            self._children.append(node)
            node.build_tree()

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