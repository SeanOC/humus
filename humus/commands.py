from optparse import OptionParser
import sys

from humus.core import Syncer

def humus_sync():
    parser = OptionParser()
    parser.add_option('-c', '--config', dest='config', action="store", type="string", default=None,
        help='The path to the configuation file humus should use.')

    (options, args) = parser.parse_args()

    if len(args) == 2:
        source = open(args[1])
        target_name = args[0]
    elif len(args) == 1:
        source = sys.stdin
        target_name = args[0]
    else:
        print "You must provide a target name for the file to be uploaded."
        exit(1)

    syncer = Syncer(config_path=options.config)
    syncer.sync(source=source, target_name=target_name)
    syncer.trim()
    syncer.cleanup()