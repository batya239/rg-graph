#!/usr/bin/python
# -*- coding: utf8
import os
from os import path

import graph_state
import rggraphutil.ref as ref

import graphine
import common_storage


__author__ = 'daddy-bear'


_V_STORAGE_REF = ref.Ref.create()
_R_STORAGE_REF = ref.Ref.create()
_R1_STORAGE_REF = ref.Ref.create()
_KR1_STORAGE_REF = ref.Ref.create()
_IR_C_OPERATION_STORAGE_REF = ref.Ref.create()

_STORAGE_PATH = "~/.rg-graph-storage/"
#V means "VALUE" - it's graph value
_V_STORAGE_FILE_NAME = "value_storage.py"
_R_STORAGE_FILE_NAME = "r_storage.py"
_R1_STORAGE_FILE_NAME = "rprime_storage.py"
_KR1_STORAGE_FILE_NAME = "krprime_storage.py"
_IR_C_OPERATION_STORAGE_FILE_NAME = "ir_c_operation_storage.py"


def checkInitialized():
    if not _V_STORAGE_REF.get() or not _R_STORAGE_REF.get() or not _R1_STORAGE_REF.get() or not _KR1_STORAGE_REF.get():
        raise AssertionError


def initStorage(theoryName, exprSerializer, graphStorageUseFunctions=False):
    _V_STORAGE_REF.set(_GraphValueStorage(theoryName, _STORAGE_PATH, _V_STORAGE_FILE_NAME, withFunctions=graphStorageUseFunctions))
    _R_STORAGE_REF.set(_MercurialGraphOperationValuesStorage(theoryName, 1, _STORAGE_PATH, _R_STORAGE_FILE_NAME, exprSerializer))
    _R1_STORAGE_REF.set(_MercurialGraphOperationValuesStorage(theoryName, 1, _STORAGE_PATH, _R1_STORAGE_FILE_NAME, exprSerializer))
    _KR1_STORAGE_REF.set(_MercurialGraphOperationValuesStorage(theoryName, 1, _STORAGE_PATH, _KR1_STORAGE_FILE_NAME, exprSerializer))
    _IR_C_OPERATION_STORAGE_REF.set(_MercurialGraphOperationValuesStorage(theoryName, 1, _STORAGE_PATH, _IR_C_OPERATION_STORAGE_FILE_NAME, exprSerializer))


def is_enabled():
    return _V_STORAGE_REF.get() and _R_STORAGE_REF.get() and _R1_STORAGE_REF.get() and _KR1_STORAGE_REF.get()


def putGraph(graph, expression, methodName, description=""):
    _V_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getGraph(graph, defaultValue=None):
    return _V_STORAGE_REF.get().getValue(graph, defaultValue)


def hasGraph(graph):
    return _V_STORAGE_REF.get().hasGraph(graph)


def putGraphR(graph, expression, methodName, description=""):
    _R_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getR(graph, defaultValue=None):
    return _R_STORAGE_REF.get().getValue(graph, defaultValue)


def putGraphR1(graph, expression, methodName, description=""):
    _R1_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getR1(graph, defaultValue=None):
    return _R1_STORAGE_REF.get().getValue(graph, defaultValue)


def putGraphKR1(graph, expression, methodName, description=""):
    _KR1_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getKR1(graph, defaultValue=None):
    return _KR1_STORAGE_REF.get().getValue(graph, defaultValue)


def putDeltaIR(graph, expression, methodName, description=""):
    _IR_C_OPERATION_STORAGE_REF.get().putGraph(graph, expression, methodName, description)


def getDeltaIR(graph, defaultValue=None):
    _IR_C_OPERATION_STORAGE_REF.get().getValue(graph, defaultValue)


def closeStorage(revert=False, doCommit=False, commitMessage=None):
    if commitMessage is None:
        commitMessage = "no commit message"
    _V_STORAGE_REF.get().close(revert, doCommit, "value storage: [" + commitMessage + "]")
    _R_STORAGE_REF.get().close(revert, doCommit, "r storage: [" + commitMessage + "]")
    _R1_STORAGE_REF.get().close(revert, doCommit, "r1 storage: [" + commitMessage + "]")
    _KR1_STORAGE_REF.get().close(revert, doCommit, "kr1 storage [" + commitMessage + "]")
    _IR_C_OPERATION_STORAGE_REF.get().close(revert, doCommit, "ir c operation storage [" + commitMessage + "]")


class _MercurialGraphOperationValuesStorage(common_storage.AbstractMercurialAwareStorage):
    def __init__(self, theoryName, theoryIndex, storagePath, storageFileName, exprSerializer):
        super(_MercurialGraphOperationValuesStorage, self).__init__(theoryName, theoryIndex, storagePath, storageFileName)
        self._exprSerializer = exprSerializer

    def putGraph(self, graph, expression, methodName, description=""):
        if self._checkExist(graph, methodName, description):
            return
        value = (expression, methodName, description)
        gs = str(graph.toGraphState())
        self._underlying[gs].append(value)
        self._flushRawStorage.append("\nstorage[\"" + gs + "\"].append(("
                                     + self._exprSerializer(str(value[0].simplify_indexed()))
                                     + ", \"" + self._theoryName
                                     + "\", \"" + value[1]
                                     + "\", \"" + value[2] + "\"))")

    def getValue(self, graph, defaultValue=None):
        return self._underlying.get(str(graph.toGraphState()), defaultValue)

    def _flush(self, storageFile):
        for rawData in self._flushRawStorage:
            storageFile.write(rawData)

    def _checkExist(self, graph, methodName, description):
        value = self.getValue(graph)
        if value is None:
            return False
        for v in value:
            if v[1] == methodName and v[2] == description:
                return True
        return False


class _GraphValueStorage(common_storage.AbstractMercurialAwareStorage):
    _FUNCTIONS_FOLDER_NAME = "fun"

    def __init__(self, theoryName, storagePath, storageFileName, canCalculateGraphChecker=(lambda g: False), withFunctions=False):
        super(_GraphValueStorage, self).__init__(theoryName, 2, storagePath, storageFileName)
        self._funUnderlying = dict() if withFunctions else None
        self._unCalculatedPos = set()
        self._unCalculatedNeg = set()
        self._canCalculateGraphCheckerWrapper = self.wrapChecker(canCalculateGraphChecker)
        if withFunctions:
            self._initFunctionsStorage(storagePath)

    def _initFunctionsStorage(self, storagePath):
        funStoragePath = path.join(path.expanduser(storagePath), _GraphValueStorage._FUNCTIONS_FOLDER_NAME)
        prefix = "STORAGE_" + self._theoryName
        if path.exists(funStoragePath):
            for fileName in os.listdir(funStoragePath):
                if fileName.startswith(prefix):
                    functionName = "__" + fileName[len(prefix) + 1:-3]
                    functionPath = path.join(funStoragePath, fileName)
                    self._funUnderlying[functionName] = functionPath

    def getValue(self, graph, defaultValue=None):
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
                    return [result]
        if self._canCalculateGraphCheckerWrapper(graph, graphState):
            return self.createUnCalculatedValue(graphState)
        return defaultValue

    def putGraph(self, graph, expression, methodName, description="", force=False):
        assert isinstance(graph, graphine.Graph)
        if not force and self.hasGraph(graph):
            return
        assert len(expression) == 2
        pPower = expression[1]
        assert isinstance(pPower, tuple) or isinstance(pPower, graph_state.Rainbow)
        assert len(pPower) == 2
        graphStateAsString = str(graph)
        firstAsString = str(expression[0])
        self._underlying[graphStateAsString].append((firstAsString, pPower, self._theoryName))
        self._flushRawStorage.append("\nstorage[\"" + graphStateAsString + "\"].append((\"" + firstAsString
                             + "\", " + str(pPower)
                             + ", \"" + self._theoryName + "\", \"" + methodName + "\", \"" + description + "\"))")

    def _flush(self, storageFile):
        for rawData in self._flushRawStorage:
            storageFile.write(rawData)

    def hasGraph(self, graph):
        graphState = graph.toGraphState()
        hasInStorage = str(graphState) in self._underlying
        if hasInStorage:
            return True
        if self._funUnderlying:
            for function in self._funUnderlying.items():
                execfile(function[1])
                result = locals()[function[0]](graph)
                if result:
                    self.putGraph(graph, result, function[0], force=True)
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