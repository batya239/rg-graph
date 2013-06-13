import os
import shutil
import unittest
import graph_storage
import rprime_storage

__author__ = 'dima'


class GraphStorageAwareTestCase(unittest.TestCase):
    def setUp(self):
        self._deleteStorageDir()
        graph_storage.initStorage(withFunctions=True)
        rprime_storage.initStorage()

    def tearDown(self):
        self._deleteStorageDir()
        rprime_storage.closeStorage(revert=True)

    def _deleteStorageDir(self):
        baseStoragePath = os.path.join(os.getcwd(), graph_storage._STORAGE_FILE_NAME)
        if os.path.exists(baseStoragePath):
            os.remove(baseStoragePath)
        storageDirPath = os.path.join(os.getcwd(), graph_storage._STORAGE_FOLDER)
        if os.path.exists(storageDirPath):
            shutil.rmtree(storageDirPath)