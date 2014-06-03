#!/usr/bin/python
# -*- coding: utf8

__author__ = 'dima'

import pymongo
import logging


class GraphIdExtractor(object):
    def get_id(self, graph, collection_name):
        pass


class StrGraphIdExtractor(GraphIdExtractor):
    def get_id(self, graph, collection_name):
        return str(graph)


class MongoClientWrapper(object):
    def __init__(self,
                 host_name="localhost",
                 port=27017,
                 db_name=None,
                 graph_id_extractor=None):
        assert db_name is not None
        self._client = pymongo.MongoClient(host_name, port)
        self._db = self._client[db_name]
        self._collections = dict()
        self._graph_id_extractor = graph_id_extractor if graph_id_extractor is not None else StrGraphIdExtractor()

    def get_graph(self, collection, graph, condition=None):
        condition = dict() if condition is None else dict(condition)
        condition["_id"] = str(graph)
        return self._db[collection].find_one(condition)["value"]

    def has_graph(self, collection, graph, condition=None):
        return self.get_graph(collection, graph, condition) is not None

    def put_graph(self, collection, graph, value, condition=None):
        doc = dict() if condition is None else dict(condition)
        doc["_id"] = str(graph)
        doc["value"] = value
        self._db[collection].insert(doc)