#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'


class Ref(object):

    def __init__(self, element=None):
        self.element = element

    def get(self):
        return self.element

    def set(self, element):
        self.element = element

    @staticmethod
    def create(element=None):
        return Ref(element)

    def __str__(self):
        return "Ref(%s)" % self.element


class LazyRef(object):
    def __init__(self, a_lambda):
        self._lambda = a_lambda

    def get(self):
        if '_element' not in self.__dict__:
            self._element = self._lambda()
        return self._element
