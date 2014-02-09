__author__ = 'gleb'

import unittest

from pole_extractor import utils
import graphine


class TestSymmetries(unittest.TestCase):
    g2_1 = (('e11|e|::', 0.5), )
    g3_1 = (('e12|e2|e|::', 1.0), )

    g2_2 = (('e12|e3|33||', 0.5), ('e12|23|3|e|', 0.5))
    g3_2 = (('e12|e3|e4|44||', 1.5), ('e12|e3|34|4|e|', 3.0), ('e12|34|34|e|e|', 0.5))

    g2_3 = (('e12|23|4|45|5|e|', 0.5),  ('e12|34|35|e|55||', 0.25), ('e12|e3|44|55|5||', 0.25),
            ('e12|23|4|e5|55||', 1.0),  ('e12|e3|45|45|5||', 0.5),  ('e12|34|35|4|5|e|', 1.0),
            ('e12|34|34|5|5|e|', 0.25), ('e12|e3|34|5|55||', 0.5),  ('e12|33|44|5|5|e|', 0.125))
    g3_3 = (('e12|e3|45|46|e|66||', 1.5),  ('e12|e3|34|5|e6|66||', 3.0),  ('e12|e3|45|45|6|6|e|', 1.5),
            ('e12|34|56|e5|e6|6||', 1.0),  ('e12|33|45|6|e6|e6||', 1.5),  ('e12|23|4|e5|56|6|e|', 3.0),
            ('e12|e3|e4|45|6|66||', 1.5),  ('e12|34|35|6|e6|e6||', 1.0),  ('e12|23|4|56|56|e|e|', 1.5),
            ('e12|e3|e4|55|66|6||', 0.75), ('e12|e3|44|56|5|6|e|', 3.0),  ('e12|e3|34|5|56|6|e|', 3.0),
            ('e12|e3|45|46|5|6|e|', 6.0),  ('e12|23|4|e5|e6|66||',  1.5), ('e12|e3|e4|56|56|6||', 1.5),
            ('e12|34|35|6|e5|6|e|', 3.0),  ('e12|e3|44|55|6|6|e|', 0.75))

    def test1Loop(self):
        self.assertSetEqual(set(utils.get_diagrams(2, 1)),
                            set(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), self.g2_1)))
        self.assertSetEqual(set(utils.get_diagrams(3, 1)),
                            set(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), self.g3_1)))

    def test2Loops(self):
        self.assertSetEqual(set(utils.get_diagrams(2, 2)),
                            set(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), self.g2_2)))
        self.assertSetEqual(set(utils.get_diagrams(3, 2)),
                            set(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), self.g3_2)))

    def test3Loops(self):
        self.assertSetEqual(set(utils.get_diagrams(2, 3)),
                            set(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), self.g2_3)))
        self.assertSetEqual(set(utils.get_diagrams(3, 3)),
                            set(map(lambda x: (graphine.Graph.fromStr(x[0]), x[1]), self.g3_3)))