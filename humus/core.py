import ConfigParser
import os

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
        super(Syncer, self).__init__()


    def load_config(self):
        config = ConfigParser.SafeConfigParser()
        config.read([os.path.abspath(path) for path in self.config_paths])

        return config
