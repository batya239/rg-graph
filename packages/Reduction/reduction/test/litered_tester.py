#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import tempfile
from os import path
import os
import jrules_parser
from sector import Sector
import random
import subprocess
import unittest
import swiginac


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super(BaseTestCase, self).__init__(methodName)
        self.tester = LiteRedTester(self.get_tested_reductor(), self)

    def get_tested_reductor(self):
        raise NotImplementedError()

    def do_test(self, size):
        for i in xrange(size):
            self.tester.do_test(self.tester.create_random_sector())


class LiteRedTester(object):

    def __init__(self, tested_reductor, test_case):
        self._dir = tempfile.mkdtemp(prefix="litered_tezZ_z_Zzter")
        self._env_name = tested_reductor.env_name
        self._env_path = tested_reductor.env_path
        self._tested_reductor = tested_reductor
        self._test_case = test_case
        self._sector_size = tested_reductor.evaluate_sector_size()

    def execute_math(self, sector):
        code = _LITERED_TEMPLATE.format(sector.as_litered_representation(self._env_name),
                                        path.join(path.dirname(path.realpath(__file__)), path.pardir, self._env_path, self._env_name),
                                        self._dir)
        executable = path.join(self._dir, "test.m")
        #with open(executable, "w") as f:
        #    f.write(code)
        #call("cat %s | math" % executable)
        proc = subprocess.Popen("math", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        proc.stdin.write(code)
        proc.stdin.close()
        proc.stdout.read()
        result = dict()
        for i in (5.9, 9.9, 14.9):
            result_file_name = path.join(self._dir, "test.res%s" % i)
            with open(result_file_name, 'r') as f:
                raw_result = f.read()
                raw_result = raw_result.replace(".,", ",").replace(". ", "").replace(".*", "*").replace(".]", "]")
                r = eval(jrules_parser.convert_rule(raw_result, self._env_name))
                result[i] = r
            os.remove(path.join(self._dir, "test.res%s" % i))
        return result

    def do_test(self, sector):
        math_res = self.execute_math(sector)
        reductor_res = self._tested_reductor.evaluate_sector(sector)
        for k, v in math_res.items():
            self._test_case.assertTrue(LiteRedTester.check_sector_linear_combinations(v - reductor_res.evaluate(_d=k)),
                                       "\nexpected: %s\nactual: %s\ndiff: %s" % (v,
                                                                                 reductor_res.evaluate(_d=k),
                                                                                 v - reductor_res.evaluate(_d=k)))

    def create_random_sector(self):
        return Sector(map(lambda x: random.randint(0, 2), xrange(self._sector_size)))

    @staticmethod
    def check_sector_linear_combinations(sectors):
        add_part = sectors.additional_part
        if abs(add_part.to_double() if isinstance(add_part, swiginac.numeric) else add_part) > 1E-6:
            return False
        for coef in sectors.sectors_to_coefficient.values():
            if abs(coef.to_double() if isinstance(coef, swiginac.numeric) else coef) > 1E-6:
                return False
        return True


_LITERED_TEMPLATE = """
<<LiteRed`

(*SetDirectory[NotebookDirectory[]];*)
SetDim[d];
Declare[{{k1, k2, k3, p}}, Vector];
sp[p, p] = 1;
<<"{1}";
expr = IBPReduce[{0}];
expr6 = N[expr/.d->5.9]>>{2}/test.res5.9
expr10 = N[expr/.d->9.9]>>{2}/test.res9.9
expr15 = N[expr/.d->14.9]>>{2}/test.res14.9
"""
