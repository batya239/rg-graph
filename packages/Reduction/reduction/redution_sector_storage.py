#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'


from rggraphenv import MongoClientWrapper, StrIdExtractor, symbolic_functions, log
from sector import Sector, d, J
import swiginac
import atexit
import subprocess


def execute_or_default(cmd, default_value):
    try:
        return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read()[:-1]
    except:
        return default_value


try:
    from revision import REVISION
except ImportError:
    REVISION = execute_or_default("hg id -i", "revision_info_is_not_exist")
USER_NAME = execute_or_default("whoami", "user_name_is_not_specified")
HOST_NAME = execute_or_default("hostname", "host_name_is_not_specified")
CONDITION = {"hg_revision": REVISION, "user": USER_NAME, "host": HOST_NAME}


class ReductionSectorStorage(object):
    COLLECTION_NAME = "cache_"

    def __init__(self, reductor_name, host_name="localhost", port=27017):
        try:
            self._storage = MongoClientWrapper(host_name, port, db_name="reduction_cache")
            self._collection_name = ReductionSectorStorage.COLLECTION_NAME + reductor_name
            atexit.register(lambda: self._storage.close())
            self._enable = True
        except Exception as e:
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
            return
        self._storage.put(self._collection_name,
                          sector,
                          symbolic_functions.to_internal_code(str(value), strong=True),
                          condition=CONDITION)