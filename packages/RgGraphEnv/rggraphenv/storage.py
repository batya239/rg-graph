#!/usr/bin/python
# -*- coding: utf8
import os
import graph_state
import graphine
import collections
import symbolic_functions
import swiginac
import inject
import rggraphutil.rg_graph_collections as rg_graph_collections
from rggraphutil import VariableAwareNumber
from subprocess import call
from os import path
import atexit


__author__ = 'daddy-bear'


_STORAGE_PATH = "~/.rg-graph-storage/"
#V means "VALUE" - it's graph value
V_STORAGE = ("value", "value_storage.py")
R_STORAGE = ("r", "r_storage.py")
R1_STORAGE = ("r1", "rprime_storage.py")
KR1_STORAGE = ("kr1", "krprime_storage.py")


class StorageSettings(object):
    def __init__(self, theory_name, method_name, description):
        self.method_name = method_name
        self.description = description
        self.theory_name = theory_name

    def on_shutdown(self, revert=False, do_commit=False, commit_message=None):
        self.revert = revert
        self.do_commit = do_commit
        self.commit_message = commit_message
        return self

    def assert_valid(self):
        assert self.revert is not None
        assert self.do_commit is not None


class StoragesHolder(object):
    def __init__(self, settings, storages=(V_STORAGE, R_STORAGE, KR1_STORAGE, R1_STORAGE)):
        settings.assert_valid()
        self._settings = settings
        self._storages = dict(map(lambda (n, file_name): (n, MercurialAwareStorage(settings.theory_name, _STORAGE_PATH, file_name)), storages))

        @atexit.register
        def dispose():
            self.close(settings.revert, settings.do_commit, settings.commit_message)

    def get_graph(self, graph, operation_name):
        return self._storages[operation_name].get_graph(graph)

    def put_graph(self, graph, expression, operation_name):
        self._storages[operation_name].put_graph(graph, expression, self._settings.method_name, self._settings.description)

    def close(self, revert=False, do_commit=False, commit_message=None):
        if commit_message is None:
            commit_message = "no commit message"
        for name, storage in self._storages.items():
            storage.close(revert, do_commit, name + " storage: [" + commit_message + "]")

    @staticmethod
    def instance():
        return inject.instance(StoragesHolder)


class AbstractGraphOperationValuesStorage(object):
    def put_graph(self, graph, expression, methodName, description=""):
        pass

    def get_graph(self, graph):
        pass


class AbstractGraphOperationValuesStorageBuilder(object):
    def build(self, operation_name):
        pass


class MercurialAwareStorage(AbstractGraphOperationValuesStorage):
    #noinspection PyUnusedLocal,PyUnresolvedReferences
    def __init__(self, theoryName, storagePath, storageFileName):
        storagePath = os.path.expanduser(storagePath)
        if not os.path.exists(storagePath):
            raise AssertionError("please checkout https://code.google.com/p/rg-graph-storage to ~/.rg-graph-storage/ firstly")
        storage = rg_graph_collections.emptyListDict()
        e = symbolic_functions.e
        p = symbolic_functions.p
        tgamma = swiginac.tgamma
        psi = swiginac.psi
        log = swiginac.log
        zeta = swiginac.zeta
        Pi = swiginac.Pi
        Euler = swiginac.Euler
        execfile(os.path.join(storagePath, storageFileName))
        self._storage_file_name = storageFileName
        self._storage_path = storagePath
        self._underlying = MercurialAwareStorage._theory_filter(theoryName, storage)
        self._flush_raw_storage = []
        self._theoryName = theoryName

    def put_graph(self, graph, expression, methodName, description=""):
        if self.get_graph(graph) is not None:
            return
        value = (expression, methodName, description)
        gs = str(graph.toGraphState())
        self._underlying[gs].append(value)

        if isinstance(expression, tuple):
            serialized = str("(" + symbolic_functions.safe_integer_numerators_strong(str(expression[0])) + ",VariableAwareNumber(\"l\"," + str(expression[1].a) + "," + str(expression[1].b) + "))")
        else:
            serialized = symbolic_functions.safe_integer_numerators_strong(str(expression))

        self._flush_raw_storage.append("\nstorage[\"" + gs + "\"].append(("
                                     + serialized
                                     + ", \"" + self._theoryName
                                     + "\", \"" + value[1]
                                     + "\", \"" + value[2] + "\"))")

    def get_graph(self, graph):
        value = self._underlying.get(str(graph.toGraphState()), None)
        if value is None:
            return None
        return value[0]

    @staticmethod
    def _theory_filter(theoryName, storage):
        filtered = rg_graph_collections.emptyListDict()
        for k, vs in storage.items():
            filtered[k] = filter(lambda v: v[1] == theoryName, vs)
        return filtered

    def close(self, revert=False, do_commit=False, commit_message=None):
        storage_file = open(os.path.join(self._storage_path, self._storage_file_name), "a")
        for raw_data in self._flush_raw_storage:
            storage_file.write(raw_data)
        storage_file.close()
        if revert:
            call("cd " + self._storage_path + "; hg revert " + self._storage_file_name, shell=True)
        if do_commit:
            if commit_message is None:
                raise ValueError("commit message must be specified")
            call("cd " + self._storage_path + "; hg commit -m \"" + commit_message + "\"", shell=True)