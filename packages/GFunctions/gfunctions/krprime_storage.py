#!/usr/bin/python
# -*- coding: utf8
import os
from subprocess import call


_STORAGE_PATH = "~/.rg-graph-storage/"
_STORAGE_FILE_NAME = "krprime_storage.py"


class _AbstractKRPrimeGraphStorage(object):
    def putGraph(self, graph, expression, methodName, description):
        pass

    def getValue(self, graph, defaultValue=None):
        pass


class _FakeKRPrimeStorage(_AbstractKRPrimeGraphStorage):
    def __init__(self):
        self._underlying = dict()

    def putGraph(self, graph, expression, methodName, description):
        self._underlying[graph] = (expression, methodName, description)

    def getValue(self, graph, defaultValue=None):
        return self._underlying.get(graph, defaultValue)


class _MercurialKRPrimeStorage(_AbstractKRPrimeGraphStorage):
    _instance = None

    # noinspection PyUnresolvedReferences,PyArgumentList
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_MercurialKRPrimeStorage, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

    def __init__(self, storagePath):
        if not os.path.exists(storagePath):
            raise AssertionError(
                "please checkout https://code.google.com/p/rg-graph-storage to ~/.rg-graph-storage/ firstly")
        else:
            call("cd " + storagePath + "; hg pull -u", shell=True)
            # noinspection PyUnusedLocal
        storage = dict()
        import symbolic_functions
        # noinspection PyUnusedLocal
        _e = symbolic_functions._getE()
        readFile = open(os.path.join(storagePath, _STORAGE_FILE_NAME), "r")
        eval([l for l in readFile])
        readFile.close()
        self._underlying = storage
        self._storageFile = open(os.path.join(storagePath, _STORAGE_FILE_NAME), "a")
        self._storagePath = storagePath

    def putGraph(self, graph, expression, methodName, description):
        value = (expression, methodName, description)
        gs = _MercurialKRPrimeStorage._shortGraphState(graph)
        self._underlying[gs] = value
        self._storageFile.write("\nstorage[" + gs + "]" + str(value))

    def getValue(self, graph, defaultValue=None):
        return self._underlying.get(_MercurialKRPrimeStorage._shortGraphState(graph), defaultValue)

    @staticmethod
    def _shortGraphState(graph):
        graphStateAsStr = str(graph.toGraphState())
        return graphStateAsStr[:graphStateAsStr.index("::")]

    def close(self, doCommitAndPush, commitMessage):
        self._storageFile.close()
        if doCommitAndPush:
            call("cd " + self._storagePath + "; hg pull -u", shell=True)
            call("cd " + self._storagePath + "; hg commit -m \"" + commitMessage + "\"", shell=True)
            call("cd " + self._storagePath + "; hg push", shell=True)


_STORAGE = None


def initStorage(unitTestMode=False):
    if unitTestMode:
        _STORAGE = _FakeKRPrimeStorage.__new__(_MercurialKRPrimeStorage)
        _STORAGE.__init__()
    else:
        _STORAGE = _MercurialKRPrimeStorage.__new__(_MercurialKRPrimeStorage)
        _STORAGE.__init__(_STORAGE_PATH)


def putGraph(graph, expression, methodName, description):
    _STORAGE.putGraph(graph, expression, methodName, description)


def getValue(graph, defaultValue=None):
    _STORAGE.getValue(graph, defaultValue)


def closeStorage(unitTestMode=False, doCommitAndPush=False, commitMessage=None):
    if not unitTestMode:
        if doCommitAndPush and commitMessage is None:
            raise ValueError("commit message must be specified")
        _STORAGE.close(doCommitAndPush, commitMessage)