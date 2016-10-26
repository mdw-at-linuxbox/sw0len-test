from swtests import (setup, teardown)
from bunch import *
from optparse import OptionParser
import traceback

options = Bunch({'cleanup': False})

def parse_options():
    parser = OptionParser()
    parser.add_option('--no-cleanup', dest='cleanup', action="store_false",
	help='turn off teardown so you can peruse the state of buckets after testing')
    parser.set_defaults(cleanup=True)
    return parser.parse_args()

def _main():
    (options, args) = parse_options()
    if options.cleanup:
	teardown()

def main():
    setup()
    try:
	_main()
    except Exception as e:
	traceback.print_exc()
	teardown()

if __name__ == '__main__':
    main()
