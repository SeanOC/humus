import os

from humus.exceptions import ConfigError

class Syncer(object):

    config_paths = [
        './humus.ini',
            '~/humus.ini',
        '/etc/humus.ini',
        '/etc/humus/humus.ini',
    ]

    def __init__(self):
        super(Syncer, self).__init__()

    def get_config_path(self):
        '''
        Find the config file for humus.
        '''
        found_path = None

        for path in self.config_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                found_path = full_path
                break

        if found_path is None:
            raise ConfigError('No configuration file could be found (tried %s).' % u', '.join(self.config_paths))

        return full_path