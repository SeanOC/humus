from unittest import TestCase

from humus.core import Syncer

class CoreTests(TestCase):

    def test_basic(self):
        syncer = Syncer()
        assert True