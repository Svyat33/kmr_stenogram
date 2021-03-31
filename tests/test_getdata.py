import os
import unittest
import mock
import mock as mock
import requests

from web.loader import LoadDocuments, Document


# from unittest.mock import Mock, patch

class TestGetData(unittest.TestCase):
    def setUp(self) -> None:
        with open(os.path.join(os.path.dirname(__file__), 'valid_page.html')) as f:
            self.valid_responce_page = f.read()
        self.invalid_responce_page = ''

    def pass_test_iterator(self):
        k = 0
        cnt = 3
        for doc in LoadDocuments(cnt):
            self.assertIsInstance(doc, Document)
            k += 1
        self.assertEqual(k, cnt)

    @mock.patch('web.loader.SiteWalk')
    def test_get_first_page_ok(self, MockSiteWalk):
        ret = mock.Mock(spec=requests.Response)
        ret.status_code = 200
        ret.content = self.valid_responce_page.encode()
        MockSiteWalk.return_value.get.return_value = ret
        itr = LoadDocuments(MockSiteWalk)
        doc = next(itr)
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.title, 'Пленарне засідання від 11.03.6621')
        self.assertEqual(doc.file_name, '11.03.2021.odt')

    @mock.patch('web.loader.SiteWalk')
    def test_get_first_page_err(self, MockSiteWalk):
        MockSiteWalk.return_value.get.side_effect = ConnectionError()
        with self.assertRaises(ConnectionError):
            itr = LoadDocuments(MockSiteWalk)
            _ = next(itr)
