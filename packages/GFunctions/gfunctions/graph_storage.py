#!/usr/bin/python
# -*- coding: utf8
from os import path
import graph_state
import graphine


class GraphStorage(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GraphStorage, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self, canCalculateGraphChecker=(lambda g: False)):
        self._underlying = dict()
        self._unCalculatedPos = set()
        self._unCalculatedNeg = set()
        self._canCalculateGraphCheckerWrapper = self.wrapChecker(canCalculateGraphChecker)

    def get(self, graph):
        graphState = graph.toGraphState()
        storageValue = self._underlying.get(str(graphState), None)
        if storageValue is not None:
            return storageValue
        if self._canCalculateGraphCheckerWrapper(graph, graphState):
            return self.createUnCalculatedValue(graphState)
        return None

    def has(self, graph):
        graphState = graph.toGraphState()
        hasInStorage = str(graphState) in self._underlying
        if hasInStorage:
            return True
        return self._canCalculateGraphCheckerWrapper(graph, graphState)

    def createUnCalculatedValue(self, graphState):
        return "G(%s)" % str(graphState)

    def wrapChecker(self, checker):
        def wrapper(graph, graphState):
            if graphState in self._unCalculatedPos:
                return True
            if graphState in self._unCalculatedNeg:
                return False
            if checker(graph):
                self._unCalculatedPos.add(graphState)
                return True
            else:
                self._unCalculatedNeg.add(graphState)
                return False

        return wrapper


def writeUnCalculatedToFile(fileName):
    aFile = open(fileName, "a")
    for gs in _STORAGE._unCalculatedPos:
        aFile.write(str(gs))
        aFile.write("\n")
    aFile.close()


def put(graphState, value):
    assert isinstance(graphState, graphine.Graph)
    assert len(value) == 2
    assert isinstance(value[0], str)
    assert isinstance(value[1], tuple)
    assert len(value[1]) == 2
    if has(graphState):
        return
    graphStateAsString = str(graphState)
    _STORAGE._underlying[graphStateAsString] = value
    storageFile = open(_STORAGE_FILE_NAME, "a")
    storageFile.write("\n")
    storageFile.write(str((graphStateAsString, value[0], value[1])))
    storageFile.close()


def get(graph):
    return _STORAGE.get(graph)


def has(graph):
    return _STORAGE.has(graph)


_STORAGE_FILE_NAME = "graph_storage.txt"

_STORAGE = GraphStorage.__new__(GraphStorage)

def initStorage(canCalculateGraphChecker=(lambda g: False)):
    _STORAGE.__init__(canCalculateGraphChecker)
    if path.exists(_STORAGE_FILE_NAME):
        for line in open(_STORAGE_FILE_NAME, "r"):
            k, v1, v2 = eval(line)
            _STORAGE._underlying[k] = (v1, v2)
    else:
        localStorageFile = open(_STORAGE_FILE_NAME, "a")
        for line in open(path.join(path.dirname(path.realpath(__file__)), _STORAGE_FILE_NAME), "r"):
            if not len(line):
                continue
            k, v1, v2 = eval(line)
            _STORAGE._underlying[k] = (v1, v2)
            localStorageFile.write(str((k, v1, v2)))
            localStorageFile.write("\n")
        localStorageFile.close()

