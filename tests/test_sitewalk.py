import unittest

import mock
from requests import Session
from unittest.mock import patch
from web.loader import SiteWalk


class TestSiteWalk(unittest.TestCase):
    @patch.object(Session, 'get')
    def test_get_ok(self, req):
        sw = SiteWalk()
        sw.get("111")
        self.assertEqual(req.call_args, mock.call('111'))

