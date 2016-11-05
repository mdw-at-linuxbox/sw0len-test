from swtests import (setup, teardown)
import swtests.test0len
import swtests.testrange
from bunch import *
from optparse import OptionParser
import traceback
import inspect

options = Bunch({'cleanup': False})

def parse_options():
    parser = OptionParser()
    parser.add_option('--no-cleanup', dest='cleanup', action="store_false",
	help='turn off teardown so you can peruse the state of buckets after testing')
    parser.set_defaults(cleanup=True)
    return parser.parse_args()

tests = [
#	('test_trivial_make_delete_container',
#		swtests.test0len.test_trivial_make_delete_container),
#	('test_read_NZ_object_byterange',
#		swtests.test0len.test_read_NZ_object_byterange),
#	('test_read_NZ_object_all_parts',
#		swtests.test0len.test_read_NZ_object_all_parts),
#	('test_read_NZ_whole_object',
#		swtests.test0len.test_read_NZ_whole_object),
#	('test_read_NZ_part_again',
#		swtests.test0len.test_read_NZ_part_again),
#	('test_read_NZ_part_yet_again',
#		swtests.test0len.test_read_NZ_part_yet_again),
#	('test_read_NZN_object_parts',
#		swtests.test0len.test_read_NZN_object_parts),
#	('test_read_NZN_object',
#		swtests.test0len.test_read_NZN_object),
#	('test_read_NZN_part_again',
#		swtests.test0len.test_read_NZN_part_again),
#	('test_read_NZ_object_byterange1',
#		swtests.test0len.test_read_NZ_object_byterange1),
#	('test_read_NZ_object_byterange2',
#		swtests.test0len.test_read_NZ_object_byterange2),
#	('test_patch_then_read_NZN_object',
#		swtests.test0len.test_patch_then_read_NZN_object),
#	('test_read_Z_object',
#		swtests.test0len.test_read_Z_object),
#	('test_read_nonexistant_object',
#		swtests.test0len.test_read_nonexistant_object),
#	('test_read_NZ_object_part_may_fail',
#		swtests.test0len.test_read_NZ_object_part_may_fail),
#	('test_read_NZ_object_part_should_work',
#		swtests.test0len.test_read_NZ_object_part_should_work),
#	('test_ends',
#		swtests.test0len.test_ends),
	('test_readZObj', swtests.testrange.testByteRange.test_readZObj),
	('test_NZobj', swtests.testrange.testByteRange.test_NZobj),
	('test_ends', swtests.testrange.testByteRange.test_ends),
	]

def _main():
    inited = {}
    for j in tests:
	print j[0] + " ...",
	try:
	    if inspect.ismethod(j[1]):
		kkk = j[1].im_class()
		if not inited.has_key(kkk):
		    kkk.setupClass()
		    inited[kkk] = True
		j[1](kkk)
	    else:
	        j[1]()
	    print "ok"
	except Exception as e:
	    print "ERROR"
    for j in inited.keys():
	j.teardownClass()

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
