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
