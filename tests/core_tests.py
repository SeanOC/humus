import ConfigParser
from copy import copy
import os
from unittest import TestCase
import bz2

from boto.s3.connection import S3Connection
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
        config.set('AWS', 'bucket', test_config['AWS']['bucket'])
        config.set('AWS', 'path', 'test')

        # Make sure that the files directory exists
        if not os.path.exists(cls.test_files_dir):
            os.mkdir(cls.test_files_dir)

        # Create the config files dir
        with open(cls.test_humus_config, 'wb') as configfile:
            config.write(configfile)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.test_humus_config)

    def tearDown(self):
        '''
        Cleanup anything that may have been put on S3.
        '''
        bucket = self.get_bucket()
        for key in bucket.list():
            key.delete()
        bucket.delete()

    def get_bucket(self):
        conn = S3Connection(test_config['AWS']['access_key'], test_config['AWS']['secret_key'])
        bucket = conn.create_bucket(test_config['AWS']['bucket'])

        return bucket

    def get_syncer(self):
        syncer = Syncer(config_paths=[self.test_humus_config,])
        return syncer

    def test_init(self):
        syncer = self.get_syncer()
        self.assertEquals(test_config['AWS']['access_key'], syncer.config.get('AWS', 'access_key'))
        self.assertEquals(test_config['AWS']['secret_key'], syncer.config.get('AWS', 'secret_key'))

    def test_cleanup(self):
        syncer = self.get_syncer()
        to_cleanup = copy(syncer.to_cleanup)

        for directory in to_cleanup:
            self.assertTrue(os.path.exists(directory))

        syncer.cleanup()

        for directory in to_cleanup:
            self.assertFalse(os.path.exists(directory))

    def test_sync(self):
        syncer = self.get_syncer()
        test_file_path = os.path.join(self.test_files_dir, 'text_file.txt')
        with open(test_file_path) as test_file:
            syncer.sync(test_file, 'text_file.txt')
            test_file.seek(0)
            expected = bz2.compress(test_file.read())

        bucket = self.get_bucket()
        key = bucket.get_key('test/text_file.txt.bz2')
        result = key.get_contents_as_string()

        self.assertEquals(expected, result)