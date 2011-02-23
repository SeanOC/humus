from bz2 import BZ2File
import ConfigParser
from datetime import datetime
import logging
import os
import shutil
import subprocess
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

    def __init__(self, config_path=None):
        if config_path is not None:
            self.config_paths = [config_path,]

        self.config = self.load_config()
        self.conn = S3Connection(self.config.get('AWS', 'access_key'), self.config.get('AWS', 'secret_key'))

        self.working_dir = tempfile.mkdtemp()
        self.to_cleanup = [self.working_dir]
        self.path = self.config.get('AWS', 'path', '')
        if self.config.has_section('humus'):
            if self.config.has_option('humus', 'chunk_size'):
                self.chunk_size = self.config.getint('humus', 'chunk_size')
            else:
                self.chunk_size = 1024
            if self.config.has_option('humus', 'count_limit'):
                self.count_limit = self.config.getint('humus', 'count_limit')
            else:
                self.count_limit = None

            if self.config.has_option('humus', 'age_limit'):
                self.age_limit = self.config.getint('humus', 'age_limit')
            else:
                self.age_limit = None

            if self.config.has_option('humus', 'compress'):
                self.compress = self.config.getboolean('humus', 'compress')
            else:
                self.compress = True
        else:
            self.chunk_size = 1024
            self.count_limit = None
            self.age_limit = None
            self.compress = True

        if self.config.has_section('encryption'):
            self.gpg_binary = self.config.get('encryption', 'gpg_binary')
            self.encrypt_command = self.config.get('encryption', 'encrypt_command', raw=True)
            self.passphrase = self.config.get('encryption', 'passphrase')
        else:
            self.gpg_binary = None
            self.encrypt_command = None
            self.passphrase = None

        super(Syncer, self).__init__()

    def get_bucket(self):
        return self.conn.create_bucket(self.config.get('AWS', 'bucket'))

    def load_config(self):
        config = ConfigParser.SafeConfigParser()
        config.read([os.path.abspath(path) for path in self.config_paths])

        return config

    def compress_data(self, source, target_name):
        if self.compress:
            tmp_file_path = os.path.join(self.working_dir, '%s.bz2' % target_name)
            target = BZ2File(tmp_file_path, mode='w')

            chunk = source.read(self.chunk_size)
            while chunk != '':
                target.write(chunk)
                chunk = source.read(self.chunk_size)

            target.close()
        else:
            tmp_file_path = os.path.join(self.working_dir, target_name)
            with open(tmp_file_path, 'wb') as target:
                chunk = source.read(self.chunk_size)
                while chunk != '':
                    target.write(chunk)
                    chunk = source.read(self.chunk_size)

        return tmp_file_path

    def encrypt_file(self, path):
        tmp_file_path = os.path.join(self.working_dir, 'encrypted_file.bz2')
        full_encrypt_cmd = self.encrypt_command.split()
        args = {
            'gpg_command': self.gpg_binary,
            'output_file': tmp_file_path,
            'input_file': path,
            'passphrase': self.passphrase,
        }
        full_encrypt_cmd = [item % args for item in full_encrypt_cmd]
        gpg_proc = subprocess.Popen(full_encrypt_cmd)
        exit_code = gpg_proc.wait()
        if exit_code != 0:
            raise Exception("Exit code for '%s' was %d" % (full_encrypt_cmd, exit_code))

        return tmp_file_path


    def sync(self, source, target_name):
        upload_path = self.compress_data(source, target_name)
        if self.gpg_binary and self.encrypt_command:
            upload_path = self.encrypt_file(upload_path)

        print upload_path
        now = self.now()
        now_str = now.strftime('%Y-%m-%dT%H:%M:%S')
        name_parts = target_name.split('.')
        if len(name_parts) > 1:
            new_name = name_parts[:-1]
            new_name.append(now_str)
            new_name.append(name_parts[-1])
            if self.compress:
                new_name.append('bz2')
        else:
            new_name = name_parts
            new_name.append(now_str)
            if self.compress:
                new_name.append('bz2')


        target_name = u'.'.join(new_name)
        bucket = self.get_bucket()
        key = Key(bucket)
        key.key = os.path.join(self.path, target_name)
        logger.info('Uploading to %s' % key.key)
        key.set_metadata('created', now_str)
        key.set_contents_from_filename(upload_path)
        key.set_acl('private')

    def trim(self):
        bucket = self.get_bucket()
        keys = list(bucket.list(prefix=self.path))
        for key in keys:
            key.open_read()
        keys.sort(key=lambda key: key.get_metadata('created'), reverse=True)
        skipped = 0
        for n, key in enumerate(keys, start=1):
            # Sometimes amazon returns "directories" as keys
            # We need to skip over those.
            if key.key.endswith('/'):
                skipped += 1
                continue
            real_n = n - skipped
            if self.count_limit and self.count_limit < real_n:
                key.delete()

            if self.age_limit:
                now = self.now()
                created_str = key.get_metadata('created')
                if created_str:
                    created = datetime.strptime(created_str, '%Y-%m-%dT%H:%M:%S')
                    age = now - created
                    if self.age_limit <= age.days:
                        key.delete()
                        print "DELETING %s for being over the age limit of %s" % (key, self.age_limit)

    def cleanup(self):
        for directory in self.to_cleanup:
            shutil.rmtree(directory)

        self.to_cleanup = []




