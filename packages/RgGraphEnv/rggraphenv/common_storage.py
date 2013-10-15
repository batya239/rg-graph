#!/usr/bin/python
# -*- coding: utf8

__author__ = 'daddy-bear'

import os
import rggraphutil.rg_graph_collections as rg_graph_collections
from subprocess import call


class AbstractGraphOperationValuesStorage(object):
    def putGraph(self, graph, expression, methodName, description=""):
        pass

    def getValue(self, graph, defaultValue=None):
        pass


class AbstractMercurialAwareStorage(AbstractGraphOperationValuesStorage):
    #noinspection PyUnusedLocal,PyUnresolvedReferences
    def __init__(self, theoryName, theoryIndex, storagePath, storageFileName):
        storagePath = os.path.expanduser(storagePath)
        if not os.path.exists(storagePath):
            raise AssertionError("please checkout https://code.google.com/p/rg-graph-storage to ~/.rg-graph-storage/ firstly")
        else:
            pass
            #call("cd " + storagePath + "; hg pull -u", shell=True)
        storageQualifiedFileName = os.path.join(storagePath, storageFileName)
        storage = rg_graph_collections.emptyListDict()
        import cas_variable_resolver
        import swiginac
        e, p = cas_variable_resolver.var("e p")
        tgamma = swiginac.tgamma
        psi = swiginac.psi
        log = swiginac.log
        zeta = swiginac.zeta
        Pi = swiginac.Pi
        Euler = swiginac.Euler
        execfile(storageQualifiedFileName)
        self._storageFileName = storageFileName
        self._storagePath = storagePath
        self._underlying = AbstractMercurialAwareStorage._theoryFilter(theoryName, theoryIndex, storage)
        self._flushRawStorage = []
        self._theoryName = theoryName

    @staticmethod
    def _theoryFilter(theoryName, theoryIndex, storage):
        filtered = rg_graph_collections.emptyListDict()
        for k, vs in storage.items():
            filtered[k] = filter(lambda v: v[theoryIndex] == theoryName, vs)
        return filtered

    def _flush(self, storageFile):
        raise NotImplementedError()

    def close(self, revert=False, doCommit=False, commitMessage=None):
        storageFile = open(os.path.join(self._storagePath, self._storageFileName), "a")
        self._flush(storageFile)
        storageFile.close()
        if revert:
            call("cd " + self._storagePath + "; hg revert " + self._storageFileName, shell=True)
        if doCommit:
            if commitMessage is None:
                raise ValueError("commit message must be specified")
                #call("cd " + self._storagePath + "; hg pull -u", shell=True)
            call("cd " + self._storagePath + "; hg commit -m \"" + commitMessage + "\"", shell=True)
            #call("cd " + self._storagePath + "; hg push", shell=True)
