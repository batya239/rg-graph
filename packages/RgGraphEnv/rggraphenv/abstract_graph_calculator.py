# !/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'


class AbstractGraphCalculator(object):
    def init(self):
        pass

    def dispose(self):
        pass

    def get_label(self):
        raise NotImplementedError

    def calculate(self, graph):
        raise NotImplementedError

    def is_applicable(self, graph):
        raise NotImplementedError