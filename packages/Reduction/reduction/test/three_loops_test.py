#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


import litered_tester
import reductor
import unittest


class ThreeLoopsTestCase(litered_tester.BaseTestCase):
    def get_tested_reductor(self):
        return reductor.THREE_LOOP_REDUCTOR

    def test_me(self):
        self.do_test(10)


if __name__ == "__main__":
    unittest.main()