#!/usr/bin/python
# -*- coding: utf8
from os import path
import os
import shutil
import graph_state
import graphine


class GraphStorage(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GraphStorage, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self, canCalculateGraphChecker=(lambda g: False), withFunctions=False):
        self._underlying = dict()
        self._funUnderlying = dict() if withFunctions else None
        self._unCalculatedPos = set()
        self._unCalculatedNeg = set()
        self._canCalculateGraphCheckerWrapper = self.wrapChecker(canCalculateGraphChecker)

    def get(self, graph):
        graphState = graph.toGraphState()
        storageValue = self._underlying.get(str(graphState), None)
        if storageValue is not None:
            return storageValue
        if self._funUnderlying:
            for function in self._funUnderlying.items():
                execfile(function[1])
                result = eval(function[0] + "(graph)")
                if result:
                    #maybe we should save this result to file storage? Ohh Fuckin Yeahh!
                    return result
        if self._canCalculateGraphCheckerWrapper(graph, graphState):
            return self.createUnCalculatedValue(graphState)
        return None

    def has(self, graph):
        graphState = graph.toGraphState()
        hasInStorage = str(graphState) in self._underlying
        if hasInStorage:
            return True
        if self._funUnderlying:
            for function in self._funUnderlying.items():
                execfile(function[1])
                if eval(function[0] + "(graph)"):
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


def put(graph, value):
    assert isinstance(graph, graphine.Graph)
    if has(graph):
        return
    assert len(value) == 2
    assert isinstance(value[1], tuple) or isinstance(value[1], graph_state.Rainbow)
    assert len(value[1]) == 2
    graphStateAsString = str(graph)
    firstAsString = str(value[0])
    _STORAGE._underlying[graphStateAsString] = firstAsString, value[1]
    storageFile = open(path.join(os.getcwd(), _STORAGE_FILE_NAME), "a")
    storageFile.write("\n")
    storageFile.write(str((graphStateAsString, firstAsString, value[1])))
    storageFile.close()


def get(graph):
    return _STORAGE.get(graph)


def has(graph):
    return _STORAGE.has(graph)


_STORAGE_FOLDER = "storage"
_STORAGE_FILE_NAME = _STORAGE_FOLDER + "/graph_storage.txt"
_FUNCTION_STORAGE_FOLDER_NAME = _STORAGE_FOLDER + "/fun"

_STORAGE = GraphStorage.__new__(GraphStorage)


def initStorage(canCalculateGraphChecker=(lambda g: False), withFunctions=False):
    _STORAGE.__init__(canCalculateGraphChecker, withFunctions)
    storageFolder = path.join(os.getcwd(), _STORAGE_FOLDER)

    if not path.exists(storageFolder):
        os.mkdir(storageFolder)

    baseStoragePath = path.join(os.getcwd(), _STORAGE_FILE_NAME)
    if path.exists(baseStoragePath):
        for line in open(baseStoragePath, "r"):
            if not len(line) or line.startswith("#"):
                continue
            k, v1, v2 = eval(line)
            _STORAGE._underlying[k] = (v1, v2)
    else:
        localStorageFile = open(baseStoragePath, "a")
        for line in open(path.join(path.dirname(path.realpath(__file__)), _STORAGE_FILE_NAME), "r"):
            if not len(line) or line.startswith("#"):
                continue
            k, v1, v2 = eval(line)
            _STORAGE._underlying[k] = (v1, v2)
            localStorageFile.write(str((k, v1, v2)))
            localStorageFile.write("\n")
        localStorageFile.close()

    funStoragePath = path.join(os.getcwd(), _FUNCTION_STORAGE_FOLDER_NAME)
    if not path.exists(funStoragePath):
        funStoragePath = path.join(path.join(path.dirname(path.realpath(__file__)), _FUNCTION_STORAGE_FOLDER_NAME))
    if withFunctions and path.exists(funStoragePath):
        p = path.join(os.getcwd(), _FUNCTION_STORAGE_FOLDER_NAME)
        if not path.exists(p):
            os.mkdir(p)

        for fileName in os.listdir(funStoragePath):
            functionName = "__" + fileName[8:-3]
            functionPath = path.join(funStoragePath, fileName)
            if p != funStoragePath:
                shutil.copyfile(functionPath,
                                path.join(os.getcwd(), _FUNCTION_STORAGE_FOLDER_NAME + "/" + fileName))
            _STORAGE._funUnderlying[functionName] = functionPath

