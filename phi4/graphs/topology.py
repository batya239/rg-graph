#!/usr/bin/python
# -*- coding:utf8
"""Module for generating of topologies of feynman graphs.
"""

import collections
import nickel


def GetTopologies(valences):
    '''Generates one particle irreducible graphs for dict of valencies to num of nodes.
    '''
    pass


NickelPool = collections.namedtuple('NickelPool', 'nickel pool')


def AddNodeFromPool(nickpool):
    node = len(nickpool.nickel)
    taken_valence = CountNode(nickpool.nickel, node)
    fake_node = CountInternalNodes(nickpool)
    for valence in nickpool.pool:
        if valence == 1:
            continue
        if valence < taken_valence:
            continue
        add_nickel = [fake_node] * (valence - taken_valence)
        new_nickel = list(nickpool.nickel) + [add_nickel]
        new_pool = dict(nickpool.pool)
        new_pool[valence] -= 1
        yield NickelPool(nickel=new_nickel, pool=new_pool)


def CountNode(nickel_list, node):
    return nickel.flatten(nickel_list).count(node)


def CountInternalNodes(nickpool):
     in_pool = sum(nickpool.pool.values()) - nickpool.pool.get(1, 0)
     in_nickel = len(nickpool.nickel)
     return in_pool + in_nickel


def RemoveFakeEdge(nickpool):
    fake_node = CountInternalNodes(nickpool)
    x, y = IndexOfNode(nickpool, fake_node)
    # Connect to external.
    if nickpool.pool.get(1, 0) > 0 and (y == 0 or nickpool.nickel[x][y - 1] == -1):
        new_nickel = list(nickpool.nickel)
        new_nickel[x][y] = -1
        new_pool = dict(nickpool.pool)
        new_pool[1] -= 1
        yield NickelPool(nickel=new_nickel, pool=new_pool)
        # Do not waste time with first node not connected to an external edge.
        if x == 0 and y == 0:
            return

    # Connect to internal.
    begin = x if y == 0 else max(x, nickpool.nickel[x][y - 1])
    end = min(fake_node, len(nickpool.nickel) + 1)
    for node in range(begin, end):
        new_nickel = list(nickpool.nickel)
        new_nickel[x][y] = node
        new_pool = dict(nickpool.pool)
        yield NickelPool(nickel=new_nickel, pool=new_pool)


def IndexOfNode(nickpool, node):
    for pos, nodes in enumerate(nickpool.nickel):
        try:
            index = nodes.index(node)
        except ValueError:
            continue
        return pos, index
    raise ValueError


if __name__ == '__main__':
    pass
