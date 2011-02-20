from bz2 import BZ2File
import ConfigParser
import os
import tempfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key
from humus.exceptions import ConfigError

class Syncer(object):

    config_paths = [
        './humus.ini',
        '~/humus.ini',
        '/etc/humus.ini',
        '/etc/humus/humus.ini',
    ]

    def __init__(self, config_paths=None):
        if config_paths is not None:
            self.config_paths = config_paths

        self.config = self.load_config()
        self.conn = S3Connection(self.config.get('AWS', 'access_key'), self.config.get('AWS', 'secret_key'))

        self.working_dir = tempfile.mkdtemp()
        self.to_cleanup = [self.working_dir]
        self.chunk_size = 1024
        super(Syncer, self).__init__()

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

    def sync(self, source, target_bucket, target_name, target_path=''):
        compressed_path = self.compress_data(source)
        target_name += '.bz2'
        bucket = self.conn.create_bucket(target_bucket)
        key = Key(bucket)
        key.key = os.path.join(target_path, target_name)
        key.set_contents_from_filename(compressed_path)
        key.set_acl('private')

    def cleanup(self):
        for directory in self.to_cleanup:
            os.removedirs(directory)

        self.to_cleanup = []




