#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

from functools import wraps
import collections


CACHE = dict()


KeyAndParams = collections.namedtuple("KeyAndParams", ["key", "params", "kwargs"])


def cached_function(some_function):
    @wraps(some_function)
    def wrapper(*params, **kwargs):
        global CACHE
        hidden_key = "_" + some_function.__module__ + "_" + some_function.__name__
        kwargs_k = frozenset(map(lambda t: t, kwargs.items())) if len(kwargs) else None
        key_and_params = KeyAndParams(hidden_key, params, kwargs_k)
        if key_and_params not in CACHE:
            CACHE[key_and_params] = some_function(*params, **kwargs)
        return CACHE[key_and_params]

    return wrapper