# !/usr/bin/python
# -*- coding: utf8
import atexit
import inject
import symbolic_functions
import mongo_storage
from repoze.lru import LRUCache
import rggraphutil


__author__ = 'daddy-bear'


class StorageSettings(object):
    def __init__(self, theory_name, method_name, description, host_name="localhost", port=27017, test=False):
        self.method_name = method_name
        self.description = description
        self.theory_name = theory_name
        self.host_name = host_name
        self.port = port
        self.test = test


class StorageHolder(object):
    def __init__(self, settings):
        self._settings = settings
        if not self._settings.test:
            db_name = settings.theory_name + "-" + settings.method_name
            self._storage = mongo_storage.MongoClientWrapper(settings.host_name, settings.port, db_name)
            self._condition = {"description": settings.description}
        self._cache = LRUCache(500)

        @atexit.register
        def dispose():
            self.close()

    def get(self, graph, operation_name):
        cached = self._cache.get((graph, operation_name), None)
        if cached is not None or self._settings.test:
            return cached
        raw_value = self._storage.get(operation_name, graph, self._condition)
        if raw_value is None:
            return None
        evaluated = symbolic_functions.evaluate_expression(raw_value)
        if isinstance(evaluated, tuple):
            value = symbolic_functions.evaluate_expression(evaluated[0]), rggraphutil.VariableAwareNumber("l", evaluated[1], evaluated[2])
        else:
            value = evaluated
        self._cache.put(graph, value)
        return value

    def put(self, graph, expression, operation_name):
        cache_key = (graph, operation_name)
        cached = self._cache.get(cache_key, None)
        if cached is not None:
            return
        self._cache.put(cache_key, expression)
        if self._settings.test:
            return
        if self._storage.get(operation_name, graph, self._condition) is not None:
            return
        if isinstance(expression, tuple):
            serialized = str((symbolic_functions.to_internal_code(str(expression[0])), expression[1].a, expression[1].b))
        else:
            serialized = symbolic_functions.to_internal_code(str(expression))
        self._storage.put(operation_name, graph, serialized, self._condition)

    def close(self):
        if not self._settings.test:
            self._cache.clear()
            self._storage.close()

    @staticmethod
    def instance():
        return inject.instance(StorageHolder)