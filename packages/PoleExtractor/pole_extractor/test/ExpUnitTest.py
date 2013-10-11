__author__ = 'gleb'

__author__ = 'gleb'

import unittest
import known
import nickel
import pole_extractor.feynman as feynman
import polynomial
import copy


def unite(seq):
    """
    turns sequence of sequences in sequence of elements of sequences, e.g.
    [[1, 2, 3], [4, 5], [6,]] -> [1, 2, 3, 4, 5, 6]
    """
    s = copy.deepcopy(seq)
    result = []
    while s:
        result.extend(s.pop(0))
    return result


class TestAnalyticalCont(unittest.TestCase):
    """
    """
    def test_principal_part(self):
        return

if __name__ == '__main__':
    unittest.main()