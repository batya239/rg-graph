#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


class AbstractManuallyDebuggableAction(object):
    def is_debug(self):
        return False

    def apply(self, o):
        if not self.is_debug():
            return self.apply_automatically(o)
        else:
            res = None
            while res is None:
                try:
                    res = self.apply_manually(o)
                except:
                    pass
            return res

    def apply_automatically(self, an_object):
        raise NotImplementedError()

    def apply_manually(self, an_object):
        raise NotImplementedError()
