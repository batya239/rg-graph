#!/usr/bin/python
# -*- coding: utf8
'''Generator of momentum conservation laws combined from simple conservation laws for each node.
'''

import _comb as comb

def Conservations(line_id_to_edge):
    """Set of all the momentum conservation laws.

    Input: dictionary of line id to edge, e.g. {1: [3, 4], 2: [8, 9]}
    Output: set of conserving line ids.
    """
    ret = set()
    conservations = GetNodesLines(line_id_to_edge)
    for n in range(1, len(conservations) + 1):
      for combination in comb.xCombinations(conservations, n):
          curr = set()
          for s in combination:
            curr.symmetric_difference_update(s)
          ret.add(frozenset(curr))
    ret.discard(frozenset([]))
    return ret


def GetNodesLines(line_id_to_edge):
    """Returns list of sets of line ids connected to each node.
    """
    node_to_line_ids = {}
    for line_id, edge in line_id_to_edge.iteritems():
        for node in edge:
            if node not in node_to_line_ids:
                node_to_line_ids[node] = set()
            node_to_line_ids[node].add(line_id)

    return node_to_line_ids.values()

