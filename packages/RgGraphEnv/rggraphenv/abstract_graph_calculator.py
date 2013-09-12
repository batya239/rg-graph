#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'


class AbstractGraphCalculator(object):
    def init(self):
        pass

    def dispose(self):
        pass

    def getLabel(self):
        raise NotImplementedError

    def calculate(self, graph):
        raise NotImplementedError

    def isApplicable(self, graph):
        raise NotImplementedError