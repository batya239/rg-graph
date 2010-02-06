#!/usr/bin/python

import nickel
import unittest

class TestNickel(unittest.TestCase):
  def testGetList(self):
    g = [[0, -1], [-1, 0]]
    self.assertEqual(nickel.Nickel(g).GetList(), [[-1, -1]])
    self.assertEqual(nickel.Nickel(g).GetString(), 'ee-')
    g.extend([[2, 1], [1, 0]])
    self.assertEqual(nickel.Nickel(g).GetList(), [[-1, -1, 1], [2]])
    self.assertEqual(nickel.Nickel(g).GetString(), 'ee1-2-')


class TestStep(unittest.TestCase):
  def compareSteps(self, l, r):
    self.assertEqual(l.curr_node, r.curr_node)
    self.assertEqual(l.free_node, r.free_node)
    self.assertEqual(l.edges, r.edges)
    self.assertEqual(l.nickel_list, r.nickel_list)
    self.assertEqual(l.node_map, r.node_map)

  def testExpand(self):
    input = nickel.Step([[-1, 0], [0, 10]], [], {}, 0, 1)
    output = nickel.Step([], [[-1, 1]], {10: 1}, 1, 2)
    l = list(input.Expand())
    self.assertEqual(len(l), 1)
    self.compareSteps(l[0], output)

    input = nickel.Step([[-1, 1], [1, 2], [1, 13], [1, 14]], [[1, 2]],
                        {10: 0, 11: 1, 12: 2}, 1, 3)
    output = nickel.Step([], [[1, 2], [-1, 2, 3, 4]],
                         {10: 0, 11: 1, 12: 2, 13: 3, 14: 4}, 2, 5)
    l = list(input.Expand())
    self.assertEqual(len(l), 2)
    self.compareSteps(l[0], output)
    

class TestUtil(unittest.TestCase):
  def testAdjacentNodes(self):
    self.assertEqual(nickel.AdjacentNodes(1, [[1, 0], [0, 2], [2,1]]),
                     [0, 2])

  def testCombinations(self):
    xcomb = nickel.Combinations
    self.assertEqual(list(xcomb([1, 2, 3], 4)), [])
    self.assertEqual(list(xcomb(('1', 2), 1)), [('1',), (2,)])
    self.assertEqual(list(xcomb([1, 2, 3], 2)),
                     [[1, 2], [1, 3],
                      [2, 1], [2, 3],
                      [3, 1], [3, 2]])

  def testPermutations(self):
    xperm = nickel.Permutations
    self.assertEqual(list(xperm([])), [[]])
    self.assertEqual(list(xperm(('1',))), [('1',)])
    self.assertEqual(list(xperm('ab')), ['ab', 'ba'])
    perm3 = [[1, 2, 3], [1, 3, 2],
             [2, 1, 3], [2, 3, 1],
             [3, 1, 2], [3, 2, 1]]
    self.assertEqual(list(xperm([1, 2, 3])), perm3)
    for p in xperm([1, 2, 3]):
      self.assertEqual(p, perm3.pop(0))


unittest.main()  # Calling from the command line invokes all tests.

#if __name__ == "__main__":
#  unittest.main()