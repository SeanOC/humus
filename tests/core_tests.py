from unittest import TestCase
import ConfigParser

from mock import Mock, patch
from nose.tools import raises

from humus.core import Syncer

class CoreTests(TestCase):
    def get_syncer(self):
        syncer = Syncer()
        return syncer

    @patch.object(ConfigParser, 'SafeConfigParser')
    def test_load_config(self, parser_mock):
        syncer = Syncer()
        config = syncer.load_config()

        assert parser_mock.called