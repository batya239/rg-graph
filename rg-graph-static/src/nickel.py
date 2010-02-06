#!/usr/bin/python

class Nickel(object):
  """Class to generate graph notations by Nickel.
  """
  def __init__(self, graph):
    self.graph = graph
    self.end_mapped = max(sum(graph, [])) + 1

  def IsExternal(self, vertex):
    return vertex < 0

  def IsInternal(self, vertex):
    return vertex >= 0 and vertex < self.end_mapped

  def IsMapped(self, vertex):
    return vertex < self.end_mapped

  def SortEdges(self, g):
    for e in g:
      e.sort(key=lambda v: v if not self.IsExternal(v) else v + 1000)
    g.sort()

  def MaxInternal(self, g):
    return max(sum(g, []), key=lambda v: v if self.IsMapped(v) else v - 1000)

  def GetList(self):
    """Generates list signature of the diagram"""
    maxv = self.MaxInternal(self.graph)
    nick = [[] for i in range(max(1, maxv))]
    for e in self.graph:
      se = sorted(e, key=lambda v: v if not self.IsExternal(v) else v + 1000)
      nick[se[0]].append(se[1])
    for vv in nick:
      vv.sort()
    return nick


class Step(object):
  def __init__(self, edges, nickel_list, node_map, curr_node, free_node):
    self.edges = edges
    self.nickel_list = nickel_list
    self.node_map = node_map
    self.curr_node = curr_node
    self.free_node = free_node

  def Expand(self):
    nodes = AdjacentNodes(self.curr_node, self.edges)
    edge_rest = [e for e in self.edges if self.curr_node not in e]
    new_nodes = [n for n in nodes if n > self.free_node]
    new_nodes = list(set(new_nodes))
    free_nodes = range(self.free_node, self.free_node + len(new_nodes))
    for perm in Permutations(free_nodes):
      node_map = dict(zip(new_nodes, perm))
      def ex(n):
        return node_map.get(n, n)

      expanded_nodes = [ex(n) for n in nodes]
      expanded_nodes.sort()
      edges = [[ex(n), ex(m)] for [n, m] in edge_rest]
      node_map.update(self.node_map)
      yield Step(edges, self.nickel_list + [expanded_nodes],
                 node_map, self.curr_node + 1,
                 self.free_node + len(new_nodes))


def AdjacentNodes(node, edges):
  nodes = []
  for e in edges:
    if e[0] == node:
      nodes.append(e[1])
    elif e[1] == node:
      nodes.append(e[0])
  return nodes


def Combinations(seq, n):
  """Generator of all the n-element combinations of the given sequence.
  """
  if n == 0:
    yield seq[0:0]
  else:
    for i in range(len(seq)):
      for tail in Combinations(seq[:i] + seq[i+1:], n - 1):
        yield seq[i:i+1] + tail


def Permutations(seq):
  """Generator of all the permutations of the given sequence.
  """
  return Combinations(seq, len(seq))


if __name__ == "__main__":
  pass
