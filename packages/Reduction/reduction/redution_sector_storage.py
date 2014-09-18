#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


from rggraphenv import MongoClientWrapper, StrIdExtractor, symbolic_functions, log
from sector import Sector, d
import swiginac
import atexit

class ReductionSectorStorage(object):
    COLLECTION_NAME = "cache_"

    def __init__(self, reductor_name, host_name="localhost", port=27017):
        try:
            self._storage = MongoClientWrapper(host_name, port, db_name="reduction_cache")
            self._collection_name = ReductionSectorStorage.COLLECTION_NAME + reductor_name
            atexit.register(lambda: self._storage.close())
            self._enable = True
        except StandardError as e:
            self._enable = False
            self._local_storage = dict()
            log.error(e.message)

    def get_sector(self, sector):
        if not self._enable:
            return self._local_storage.get(sector, None)
        raw_value = self._storage.get(self._collection_name, sector)
        return None if raw_value is None else eval(raw_value)

    def put_sector(self, sector, value):
        if not self._enable:
            self._local_storage[sector] = value
        self._storage.put(self._collection_name, sector, symbolic_functions.to_internal_code(str(value), strong=True))