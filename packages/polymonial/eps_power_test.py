#!/usr/bin/python
# -*- coding: utf8
import unittest
from packages.polymonial.eps_power import EpsPower


class EpsPowerTestCase(unittest.TestCase):
    def testIt(self):
        EpsPower(1, 2)


if __name__ == "__main__":
    unittest.main()

