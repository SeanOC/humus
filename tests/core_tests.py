from unittest import TestCase

from mock import Mock, patch
from nose.tools import raises

from humus.core import Syncer
from humus.exceptions import ConfigError


def get_exists_mock(expected_path):
    mock = Mock()
    mock.side_effect = lambda path: path == expected_path

    return mock

etc_dir_exists_mock = get_exists_mock('/etc/humus/humus.ini')

class CoreTests(TestCase):
    def get_syncer(self):
        syncer = Syncer()
        return syncer

    def test_init(self):
        syncer = self.get_syncer()

    @raises(ConfigError)
    def test_find_config_missing(self):
        syncer = self.get_syncer()
        config_path = syncer.get_config_path()

    @patch('os.path.exists', etc_dir_exists_mock)
    def test_find_config_etc_dir(self, *args, **kwargs):
        syncer = self.get_syncer()
        expected = '/etc/humus/humus.ini'
        result = syncer.get_config_path()

        self.assertEquals(expected, result)

