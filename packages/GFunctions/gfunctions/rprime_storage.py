#!/usr/bin/python
# -*- coding: utf8
import os
from subprocess import call
import rggraphutil
import symbolic_functions


_STORAGE_PATH = "~/.rg-graph-storage/"
_R1_STORAGE_FILE_NAME = "rprime_storage.py"
_K_STORAGE_FILE_NAME = "krprime_storage.py"


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


class _MercurialRPrimeStorage(_AbstractKRPrimeGraphStorage):
    def __init__(self, storagePath, storageFileName):
        storagePath = os.path.expanduser(storagePath)
        if not os.path.exists(storagePath):
            raise AssertionError(
                "please checkout https://code.google.com/p/rg-graph-storage to ~/.rg-graph-storage/ firstly")
        else:
            pass
            #call("cd " + storagePath + "; hg pull -u", shell=True)
            # noinspection PyUnusedLocal
        storage = rggraphutil.emptyListDict()
        # noinspection PyUnusedLocal
        _e = symbolic_functions._getE()
        storageQualifiedFileName = os.path.join(storagePath, storageFileName)
        execfile(storageQualifiedFileName)
        self._underlying = storage
        self._storageFile = open(storageQualifiedFileName, "a")
        self._storagePath = storagePath

    def putGraph(self, graph, expression, methodName, description=""):
        value = (expression, methodName, description)
        gs = _MercurialRPrimeStorage._shortGraphState(graph)
        self._underlying[gs] = value
        self._storageFile.write("\nstorage[\"" + gs + "\"] += " +
                                " (" + symbolic_functions.toSerializableCode(str(value[0])) + ", \"" + value[1]
                                + "\", \"" + value[2] + "\")")

    def getValue(self, graph, defaultValue=None):
        return self._underlying.get(_MercurialRPrimeStorage._shortGraphState(graph), defaultValue)

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


_R1_STORAGE_REF = rggraphutil.Ref.create()
_K_STORAGE_REF = rggraphutil.Ref.create()


def checkInitialized():
    if _R1_STORAGE_REF.get() is None or _K_STORAGE_REF.get() is None:
        raise AssertionError


def initStorage(unitTestMode=False):
    if unitTestMode:
        kStorage = _FakeKRPrimeStorage.__new__(_MercurialRPrimeStorage)
        kStorage.__init__()
        r1Storage = _FakeKRPrimeStorage.__new__(_MercurialRPrimeStorage)
        r1Storage.__init__()
    else:
        kStorage = _MercurialRPrimeStorage.__new__(_MercurialRPrimeStorage)
        kStorage.__init__(_STORAGE_PATH, _K_STORAGE_FILE_NAME)
        r1Storage = _MercurialRPrimeStorage.__new__(_MercurialRPrimeStorage)
        r1Storage.__init__(_STORAGE_PATH, _R1_STORAGE_FILE_NAME)
    _K_STORAGE_REF.set(kStorage)
    _R1_STORAGE_REF.set(r1Storage)


def putGraphR1(graph, expression, methodName, description=""):
    _R1_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getR1(graph, defaultValue=None):
    return _R1_STORAGE_REF.get().getValue(graph, defaultValue)


def putGraphK(graph, expression, methodName, description=""):
    _K_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getK(graph, defaultValue=None):
    return _K_STORAGE_REF.get().getValue(graph, defaultValue)


def closeStorage(unitTestMode=False, doCommit=False, commitMessage=None):
    if not unitTestMode:
        if doCommit and commitMessage is None:
            raise ValueError("commit message must be specified")
        _K_STORAGE_REF.get().close(doCommit, "k storage: [" + commitMessage + "]")
        _R1_STORAGE_REF.get().close(doCommit, "r1 storage [" + commitMessage + "]")