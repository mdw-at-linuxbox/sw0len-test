#
# try to read DLO objects
# with 0 segments.
#
from . import (makeconnection, flush_connection, config)
from swiftclient.exceptions import ClientException
from nose.plugins.attrib import attr
from nose.tools import (eq_ as eq, raises)
import sys

# in the below, objects are first populated in __init__.py
# make_containers_and_objects
# this will make container/myobj container/mynewobj container/myemptyobj

# trivial test - proof of concept
# make and get rid of "box"
def test_trivial_make_delete_container():
    c = makeconnection()
    e = c.put_container(config.container1)
    e = c.delete_container(config.container1)

# try to fetch a byte range.  Just try
@attr('fails_on_master')
def test_read_NZ_object_byterange():
    c = makeconnection()
    need_to_flush = True
    try:
        (rh,rc) = c.get_object(config.container2, config.myobj, headers = {'Range': 'bytes=5-20'})
	eq(rc, "rt bit of text")
	need_to_flush = False
	(rh,rc) = c.get_object(config.container2, config.myobj + "/00000001")
	eq(rc, "a short bit of text")
    finally:
        # the flush_connection here is in case this test leaves the connection broken.
	#  for the broken connection case, see read_after_error later.
	if need_to_flush:
	    flush_connection()

# fetch NZ object parts, should always work
def test_read_NZ_object_all_parts():
    flush_connection()
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.myobj + "/00000001")
    eq(rc, "a short bit of text")
    (rh,rc) = c.get_object(config.container2, config.myobj + "/00000002")
    eq(rc, "")

# fetch NZ object parts.  The first part should work even if 0lenfix is
#  not applied.  The 2nd read will fail if 0lenfix isn't applied.
def test_read_NZ_whole_object():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.myobj)
    eq(rc, "a short bit of text")
    (rh,rc) = c.get_object(config.container2, config.myobj + "/00000002")
    eq(rc, "")

# even if the previous request timed out, this one (with a new connection)
# will succeed.
def test_read_NZ_part_yet_again():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.myobj + "/00000002")
    eq(rc, "")

# read the NZN parts.  timeout will discard the connection,
# so this should always succeed.
def test_read_NZN_object_parts():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.mynewobj + "/00000001")
    eq(rc, "a short bit of text")
    (rh,rc) = c.get_object(config.container2, config.mynewobj + "/00000002")
    eq(rc, "")
    (rh,rc) = c.get_object(config.container2, config.mynewobj + "/00000003")
    eq(rc, "and another short piece of text")

# read the NZN parts.  will hang if 0lenfix not applied.
def test_read_NZN_object():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.mynewobj)
    eq(rc, "a short bit of textand another short piece of text")

# should always work, even if timeout happened before this.
def test_read_NZN_part_again():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.mynewobj + "/00000002")
    eq(rc, "")

# let's try some byte ranges on NZN.
@attr('fails_on_master')
def test_read_NZ_object_byterange1():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.mynewobj, headers = {'Range': 'bytes=0-18'})
    eq(rc, "a short bit of text")

@attr('fails_on_master')
def test_read_NZ_object_byterange2():
    c = makeconnection()
    try:
	(rh,rc) = c.get_object(config.container2, config.mynewobj, headers = {'Range': 'bytes=19-49'})
	eq(rc, "and another short piece of text")
    finally:
	flush_connection()

# make NZN object into NNN, now read should work.
def test_patch_then_read_NZN_object():
    c = makeconnection()
    e = c.put_object(config.container2, config.mynewobj + "/00000002", "something extra")
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.mynewobj)
    eq(rc, "a short bit of textsomething extraand another short piece of text")

# read Z object.  should fail unless other part of 0lenfix applied too.
def test_read_Z_object():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.myemptyobj)
    eq(rc, "")

# try to read after a reported error.  The read seems to fail w/ ssl
#  when using ssl and branch wip-rgw-openssl-4.
@attr('read_after_err')
def test_read_after_error():
    c = makeconnection()
    did_it_fail = False
    try:
	(rh,rc) = c.get_object(config.container2, "nosuchobject")
    except ClientException as e:
	did_it_fail = True
    eq(did_it_fail, True)
    (rh,rc) = c.get_object(config.container2, config.myobj + "/00000001")
    eq(rc, "a short bit of text")

# fetch valid object part again - exactly the same but should work
@attr('read_after_err')
def test_read_NZ_object_part_should_work():
    c = makeconnection()
    (rh,rc) = c.get_object(config.container2, config.myobj + "/00000001")
    eq(rc, "a short bit of text")

def test_ends():
    pass
