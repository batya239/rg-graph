import os
import shutil
import unittest
import graph_storage

__author__ = 'dima'


class GraphStorageAwareTestCase(unittest.TestCase):
    def setUp(self):
        self._deleteStorageDir()
        graph_storage.initStorage(withFunctions=True)

    def tearDown(self):
        self._deleteStorageDir()

    def _deleteStorageDir(self):
        baseStoragePath = os.path.join(os.getcwd(), graph_storage._STORAGE_FILE_NAME)
        if os.path.exists(baseStoragePath):
            os.remove(baseStoragePath)
        storageDirPath = os.path.join(os.getcwd(), graph_storage._STORAGE_FOLDER)
        if os.path.exists(storageDirPath):
            shutil.rmtree(storageDirPath)