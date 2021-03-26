import unittest

from ..loader import LoadDocuments, Document


# from unittest.mock import Mock, patch

class TestGetData(unittest.TestCase):

    def test_iterator(self):
        k = 0
        cnt = 3
        for doc in LoadDocuments(cnt):
            self.assertIsInstance(doc, Document)
            k += 1
        self.assertEqual(k, cnt)
