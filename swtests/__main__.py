from swtests import (setup, teardown)
import swtests.test0len
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

tests = [
	('test_trivial_make_delete_container',
		swtests.test0len.test_trivial_make_delete_container),
	('test_read_NZ_object_byterange',
		swtests.test0len.test_read_NZ_object_byterange),
	('test_read_NZ_object_parts',
		swtests.test0len.test_read_NZ_object_parts),
	('test_read_NZ_whole_object',
		swtests.test0len.test_read_NZ_whole_object),
	('test_read_NZ_part_again',
		swtests.test0len.test_read_NZ_part_again),
	('test_read_NZ_part_yet_again',
		swtests.test0len.test_read_NZ_part_yet_again),
	('test_read_NZN_object_parts',
		swtests.test0len.test_read_NZN_object_parts),
	('test_read_NZN_object',
		swtests.test0len.test_read_NZN_object),
	('test_read_NZN_part_again',
		swtests.test0len.test_read_NZN_part_again),
	('test_read_NZ_object_byterange1',
		swtests.test0len.test_read_NZ_object_byterange1),
	('test_read_NZ_object_byterange2',
		swtests.test0len.test_read_NZ_object_byterange2),
	('test_patch_then_read_NZN_object',
		swtests.test0len.test_patch_then_read_NZN_object),
	('test_read_Z_object',
		swtests.test0len.test_read_Z_object),
	('test_ends',
		swtests.test0len.test_ends),
	]

def _main():
    for j in tests:
	if j[0] == 'test_read_NZ_object_byterange':
	    pass
	else:
	    if j[0] != 'test_read_NZ_object_parts':
		print j[0] + " (skipped)"
		continue
	print j[0] + " ...",
	try:
	    j[1]()
	    print "ok"
	except Exception as e:
	    print "ERROR"

def main():
    (options, args) = parse_options()
    try:
        setup()
	_main()
    except Exception as e:
	traceback.print_exc()
    finally:
	if options.cleanup:
	    teardown()

if __name__ == '__main__':
    main()
