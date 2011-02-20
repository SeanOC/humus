import ConfigParser
import os
from unittest import TestCase

from mock import Mock, patch
from nose.tools import raises
from testconfig import config as test_config

from humus.core import Syncer

class CoreTests(TestCase):
    test_files_dir = os.path.join(os.path.dirname(__file__), 'files')
    test_humus_config = os.path.join(test_files_dir, 'humus.ini')

    @classmethod
    def setupClass(cls):
        # Build the expected humus config file
        config = ConfigParser.SafeConfigParser()
        config.add_section('AWS')
        config.set('AWS', 'access_key', test_config['AWS']['access_key'])
        config.set('AWS', 'secret_key', test_config['AWS']['secret_key'])

        # Make sure that the files directory exists
        if not os.path.exists(cls.test_files_dir):
            os.mkdir(cls.test_files_dir)

        # Create the config files dir
        with open(cls.test_humus_config, 'wb') as configfile:
            config.write(configfile)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_humus_config)

    def get_syncer(self):

        syncer = Syncer(config_paths=[self.test_humus_config,])
        return syncer

    def test_init(self):
        syncer = self.get_syncer()


    @patch.object(ConfigParser, 'SafeConfigParser')
    def test_load_config(self, parser_mock):
        syncer = Syncer()
        config = syncer.load_config()

        assert parser_mock.called