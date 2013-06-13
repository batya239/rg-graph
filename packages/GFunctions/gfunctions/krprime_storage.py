#!/usr/bin/python
# -*- coding: utf8
import os
from subprocess import call
import rggraphutil
import symbolic_functions


_STORAGE_PATH = "~/.rg-graph-storage/"
_STORAGE_FILE_NAME = "krprime_storage.py"


class _AbstractKRPrimeGraphStorage(object):
    _instance = None

    # noinspection PyUnresolvedReferences,PyArgumentList
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_AbstractKRPrimeGraphStorage, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance

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
    def __init__(self, storagePath):
        storagePath = os.path.expanduser(storagePath)
        if not os.path.exists(storagePath):
            raise AssertionError(
                "please checkout https://code.google.com/p/rg-graph-storage to ~/.rg-graph-storage/ firstly")
        else:
            pass
            #call("cd " + storagePath + "; hg pull -u", shell=True)
            # noinspection PyUnusedLocal
        storage = dict()
        # noinspection PyUnusedLocal
        _e = symbolic_functions._getE()
        execfile(os.path.join(storagePath, _STORAGE_FILE_NAME))
        self._underlying = storage
        self._storageFile = open(os.path.join(storagePath, _STORAGE_FILE_NAME), "a")
        self._storagePath = storagePath

    def putGraph(self, graph, expression, methodName, description):
        value = (expression, methodName, description)
        gs = _MercurialKRPrimeStorage._shortGraphState(graph)
        self._underlying[gs] = value
        self._storageFile.write("\nstorage[\"" + gs + "\"] = " +
                                " (" + symbolic_functions.toSerializableCode(str(value[0])) + ", \"" + value[1]
                                + "\", \"" + value[2] + "\")")

    def getValue(self, graph, defaultValue=None):
        return self._underlying.get(_MercurialKRPrimeStorage._shortGraphState(graph), defaultValue)

    @staticmethod
    def _shortGraphState(graph):
        graphStateAsStr = str(graph.toGraphState())
        return graphStateAsStr[:graphStateAsStr.index("::")]

    def close(self, doCommit, commitMessage):
        self._storageFile.close()
        if doCommit:
            #call("cd " + self._storagePath + "; hg pull -u", shell=True)
            call("cd " + self._storagePath + "; hg commit -m \"" + commitMessage + "\"", shell=True)
            #call("cd " + self._storagePath + "; hg push", shell=True)


_STORAGE_REF = rggraphutil.Ref.create()


def initStorage(unitTestMode=False):
    if unitTestMode:
        storage = _FakeKRPrimeStorage.__new__(_MercurialKRPrimeStorage)
        storage.__init__()
    else:
        storage = _MercurialKRPrimeStorage.__new__(_MercurialKRPrimeStorage)
        storage.__init__(_STORAGE_PATH)
    _STORAGE_REF.set(storage)


def putGraph(graph, expression, methodName, description):
    _STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getValue(graph, defaultValue=None):
    return _STORAGE_REF.get().getValue(graph, defaultValue)


def closeStorage(unitTestMode=False, doCommit=False, commitMessage=None):
    if not unitTestMode:
        if doCommit and commitMessage is None:
            raise ValueError("commit message must be specified")
        _STORAGE_REF.get().close(doCommit, commitMessage)