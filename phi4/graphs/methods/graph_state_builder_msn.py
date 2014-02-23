#!/usr/bin/python
# -*- coding: utf8
__author__ = 'mkompan'

from graph_state import PropertiesConfig, GraphState, PropertyKey, PropertyExternalizer


class MSNIndex(object):
    """
    msn index for sector decomposition, assumed to  be tuple of a number of 'm', 's', 'n' in some order
    """
    EXTERNAL = 0

    class Externalizer(PropertyExternalizer):
        def deserialize(self, string):
            return MSNIndex(string)

    def __init__(self, msn):
        if isinstance(msn, str):
            self._msn = tuple(msn)
        else:
            self._msn = msn

    def make_external(self, nodes, external_node):
        """
        этот метод надо реализовать, если ты хочешь, чтобы автоматически свойство автоматически менялось, если еджа внешняя
        """
        return MSNIndex(())

    @property
    def msn(self):
        return ''.join(self._msn)

    def __cmp__(self, other):
        return cmp(self.msn, other.msn)

    def __hash__(self):
        return hash(self.msn)

    def __str__(self):
        return ''.join(self.msn)

    __repr__ = __str__

    @staticmethod
    def externalizer():
        return MSNIndex.Externalizer()


gs_builder = PropertiesConfig.create(PropertyKey(name="msn",
                                                 is_directed=False,
                                                 externalizer=MSNIndex.externalizer()))
gs_builder.GraphState = GraphState

if __name__ == "__main__":
    edges = [([-1, 0], ()), ([0, 1], ('m','s')), ([0, 1], ('s','m')), ([-1, 1], ())]
    edges_gs = list()
    for edge, msn in edges:
        edges_gs.append(gs_builder.new_edge(edge, msn=MSNIndex(msn)))
    gs = gs_builder.GraphState(edges_gs)

    print gs