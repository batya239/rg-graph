# !/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import pymongo


class IdExtractor(object):
    def get_id(self, obj, collection_name):
        pass


class StrIdExtractor(IdExtractor):
    def get_id(self, obj, collection_name):
        return str(obj)


class MongoClientWrapper(object):
    def __init__(self,
                 host_name="localhost",
                 port=27017,
                 db_name=None,
                 id_extractor=None):
        assert db_name is not None
        self._client = pymongo.MongoClient(host_name, port)
        self._db = self._client[db_name]
        self._collections = dict()
        self._id_extractor = id_extractor if id_extractor is not None else StrIdExtractor()

    def get(self, collection, obj, condition=None):
        condition = dict() if condition is None else dict(condition)
        condition["_id"] = self._id_extractor.get_id(obj, collection)
        doc = self._db[collection].find_one(condition)
        return None if doc is None else doc["value"]

    def has(self, collection, obj, condition=None):
        return self.get(collection, obj, condition) is not None

    def put(self, collection, obj, value, condition=None):
        doc = dict() if condition is None else dict(condition)
        doc["_id"] = self._id_extractor.get_id(obj, collection)
        doc["value"] = value
        self._db[collection].insert(doc)

    def close(self):
        return self._client.close()