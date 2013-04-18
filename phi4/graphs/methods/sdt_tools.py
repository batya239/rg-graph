#!/usr/bin/python
# -*- coding: utf8
import copy

__author__ = 'mkompan'


class Tree(object):
    def __init__(self, node):
        self.node = node
        self.branches = list()

    def setBranches(self, branches):
        self.branches = list()
        for branch in branches:
            if isinstance(branch, Tree):
                self.branches.append(branch)
            else:
                self.branches.append(Tree(branch))


def internalEdges(graph):
    res = list()
    for edge in graph.allEdges():
        if graph.externalVertex not in edge.nodes:
            res.append(edge)
    return res


def internalEdgesIndexed(graph):
    res = list()
    for edge in graph.allEdges(withIndex=True):
        if graph.externalVertex not in edge.underlying.nodes:
            res.append(edge)
    return res


def findCoveringSubgraphs(subgraphsIntEdges):
    res = dict()
    if len(subgraphsIntEdges)==0:
        return res
    subgraphsAsList_ = map(tuple, subgraphsIntEdges)
    for subgraph in sorted(subgraphsAsList_, key=len, reverse=True) :
        covers = False
        for subgraph_ in res:
            intersect = set(subgraph) & set(subgraph_)
            if intersect == set(subgraph):
                res[subgraph_].append(subgraph)
                covers = True
            elif intersect == set(subgraph_):
                res[subgraph] = [subgraph_] + res[subgraph_]
                del res[subgraph_]
                covers = True
        if not covers:
            res[subgraph] = list()
    return res


def subgraphTree(subgraphsIntEdges, tree=None):
    if tree is None:
        tree = Tree(None)
    branches = tree.branches
    subgraphsIntEdges_ = sorted(map(tuple, subgraphsIntEdges), key=len, reverse=True)
    for subgraph in subgraphsIntEdges_:
        covers = False

        for branch in branches:
            subgraph_ = branch.node
            intersect = set(subgraph) & set(subgraph_)
            if intersect == set(subgraph):
                branches.append(Tree(subgraph))
                covers = True
            elif intersect == set(subgraph_):
                newbranch = Tree(subgraph)
                oldBranches = branch.branches
                newbranch.setBranches()
                res[subgraph] = [subgraph_] + res[subgraph_]
                del res[subgraph_]
                covers = True
        if not covers:
            res[subgraph] = list()










