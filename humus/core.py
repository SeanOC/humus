from bz2 import BZ2File
import ConfigParser
from datetime import datetime
import logging
import os
import tempfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from humus.exceptions import ConfigError

logger = logging.getLogger('humus.Syncer')

class Syncer(object):

    config_paths = [
        './humus.ini',
        '~/humus.ini',
        '/etc/humus.ini',
        '/etc/humus/humus.ini',
    ]

    @classmethod
    def now(cls):
        '''
        Wrapper for datetime.utcnow which allows the called to be mocked in testing
        '''
        return datetime.utcnow()

    def __init__(self, config_paths=None):
        if config_paths is not None:
            self.config_paths = config_paths

        self.config = self.load_config()
        self.conn = S3Connection(self.config.get('AWS', 'access_key'), self.config.get('AWS', 'secret_key'))

        self.working_dir = tempfile.mkdtemp()
        self.to_cleanup = [self.working_dir]
        self.path = self.config.get('AWS', 'path', '')
        if self.config.has_section('humus'):
            self.chunk_size = self.config.getint('humus', 'chunk_size', 1024)
            self.count_limit = self.config.getint('humus', 'count_limit', None)
            self.age_limit = self.config.getint('humus', 'age_limit', None)
        else:
            self.chunk_size = 1024
            self.count_limit = None
            self.age_limit = None

        super(Syncer, self).__init__()

    def get_bucket(self):
        return self.conn.create_bucket(self.config.get('AWS', 'bucket'))

    def load_config(self):
        config = ConfigParser.SafeConfigParser()
        config.read([os.path.abspath(path) for path in self.config_paths])

        return config

    def compress_data(self, source):
        tmp_file_path = os.path.join(self.working_dir, 'compessed_file.bz2')
        target = BZ2File(tmp_file_path, mode='w')

        chunk = source.read(self.chunk_size)
        while chunk != '':
            target.write(chunk)
            chunk = source.read(self.chunk_size)

        target.close()

        return tmp_file_path

    def sync(self, source, target_name):
        compressed_path = self.compress_data(source)
        now = self.now()
        now_str = now.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        target_name += '.%s.bz2' % now_str
        bucket = self.get_bucket()
        key = Key(bucket)
        key.key = os.path.join(self.path, target_name)
        logger.info('Uploading to %s' % key.key)
        key.set_metadata('created', now_str)
        key.set_contents_from_filename(compressed_path)
        key.set_acl('private')

    def trim(self):
        bucket = self.get_bucket()
        keys = bucket.list(prefix=self.path)

        for n, key in enumerate(keys, start=1):

            if self.count_limit and self.count_limit > n:
                key.delete()

            if self.age_limit:
                key.open_read()
                now = self.now()
                created_str = key.get_metadata('created')
                if created_str:
                    created = datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%S.000Z')
                    age = now - created
                    if self.age_limit <= age.days:
                        key.delete()

    def cleanup(self):
        for directory in self.to_cleanup:
            os.removedirs(directory)

        self.to_cleanup = []




