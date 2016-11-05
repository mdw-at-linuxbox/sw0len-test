#
# try to read regular objects
# with byte ranges.
#
from . import (makeconnection, flush_connection, config)
from swiftclient.exceptions import ClientException
from nose.plugins.attrib import attr
from nose.tools import (eq_ as eq, raises)
import unittest
import sys

# in the below, objects are first populated in __init__.py
# make_containers_and_objects
# this will make container/myobj container/mynewobj container/myemptyobj

@attr('range')
class testByteRange:
    @classmethod
    def setupClass(cls):
	c = makeconnection()
	cls.zobject = "Zobject"
	cls.nzobject = "NZobject"
	e = c.put_object(config.container2, cls.zobject)
	e = c.put_object(config.container2, cls.nzobject,
	    "Extinct nektonic carnivore swimming in the open shallow seas of Kansas")
	pass

    @classmethod
    def teardownClass(cls):
	pass

    # read a 0 length object.  should succeed
    def test_00_readZObj(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, self.zobject)
	eq(c.c.resp.status, 200)
	eq(c.c.resp.headers['etag'], 'd41d8cd98f00b204e9800998ecf8427e')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers.__contains__('Content-Range'), False)
	eq(rc,"")

    # read a nz length object.  should succeed
    def test_01_NZobj(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, self.nzobject)
	eq(c.c.resp.status, 200)
	eq(c.c.resp.headers['etag'], '7f665836d04002a9b4a132e72e944165')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers.__contains__('Content-Range'), False)
	eq(rc,"Extinct nektonic carnivore swimming in the open shallow seas of Kansas")

    # read byterange at start of a z length object.  should 416
    def test_02_readZObj_r0(self):
	c = makeconnection()
	oops = True
	try:
	    (rh, rc) = c.get_object(config.container2, self.zobject, headers = {'Range': 'bytes=0-512'})
	except ClientException as e:
	    eq(c.c.resp.status, 416)
	    oops = False
	eq(oops,False)

    # read byterange way past start of a z length object.  should 416
    def test_03_readZObj_r1(self):
	c = makeconnection()
	oops = True
	try:
	    (rh, rc) = c.get_object(config.container2, self.zobject, headers = {'Range': 'bytes=512-1024'})
	except ClientException as e:
	    eq(c.c.resp.status, 416)
	    oops = False
	eq(oops,False)

    # read byterange at start of a nz length object.  should succeed
    def test_04_NZobj_r0(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, self.nzobject, headers = {'Range': 'bytes=0-512'})
	eq(c.c.resp.status, 206)
	eq(c.c.resp.headers['etag'], '7f665836d04002a9b4a132e72e944165')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers['Content-Range'], 'bytes 0-69/70')
	eq(rc,"Extinct nektonic carnivore swimming in the open shallow seas of Kansas")

    # read byterange at start of a nz length object.  should succeed
    def test_05_NZobj_r0(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, self.nzobject, headers = {'Range': 'bytes=0-10'})
	eq(c.c.resp.status, 206)
	eq(c.c.resp.headers['etag'], '7f665836d04002a9b4a132e72e944165')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers['Content-Range'], 'bytes 0-10/70')
	eq(rc,"Extinct nek")

    # read byterange way past end of nz length object.  should 416
    def test_06_NZobj_r1(self):
	c = makeconnection()
	oops = True
	try:
	    (rh, rc) = c.get_object(config.container2, self.nzobject, headers = {'Range': 'bytes=512-1024'})
	except ClientException as e:
	    eq(c.c.resp.status, 416)
	    oops = False
	eq(oops,False)

    # read byterange overlapping end of nz length object.  should succeed, partial read
    def test_07_NZobj_r2(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, self.nzobject, headers = {'Range': 'bytes=5-90'})
	eq(c.c.resp.status, 206)
	eq(c.c.resp.headers['etag'], '7f665836d04002a9b4a132e72e944165')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers['Content-Range'], 'bytes 5-69/70')
	eq(rc,"ct nektonic carnivore swimming in the open shallow seas of Kansas")

    # read all of NZ dlo.  should succeed
    def test_08_NZobj_dlo(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, config.myobj)
	eq(c.c.resp.status, 200)
	eq(c.c.resp.headers['etag'], '"42450929f2f6ade2c2352e7e7030407d"')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers.__contains__('Content-Range'), False)
	eq(rc,"a short bit of text")

    # read byterange at start of NZ dlo.  should succeed.
    def test_09_NZobj_dlo_r0(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, config.myobj, headers = {'Range': 'bytes=0-512'})
	eq(c.c.resp.status, 206)
	eq(c.c.resp.headers['etag'], '"42450929f2f6ade2c2352e7e7030407d"')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers['Content-Range'], 'bytes 0-18/19')
	eq(rc,"a short bit of text")

    # read byterange way past end of NZ dlo.  should 416
    def test_10_NZobj_dlo_r1(self):
	c = makeconnection()
	oops = True
	try:
	    (rh, rc) = c.get_object(config.container2, config.myobj, headers = {'Range': 'bytes=512-1024'})
	except ClientException as e:
	    eq(c.c.resp.status, 416)
	    oops = False
	eq(oops,False)

    # read byterange way past end of NZ dlo.  should 416
    def test_11_NZobj_dlo_r2(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, config.myobj, headers = {'Range': 'bytes=5-90'})
	eq(c.c.resp.status, 206)
	eq(c.c.resp.headers['etag'], '"42450929f2f6ade2c2352e7e7030407d"')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers['Content-Range'], 'bytes 5-18/19')
	eq(rc,"rt bit of text")

    # read a 0 length object.  should succeed
    def test_12_readZObj_dlo(self):
	c = makeconnection()
	(rh, rc) = c.get_object(config.container2, config.myemptyobj)
	eq(c.c.resp.status, 200)
	eq(c.c.resp.headers['etag'], '"74be16979710d4c4e7c6647856088456"')
	eq(c.c.resp.headers['content-type'], 'binary/octet-stream')
	eq(c.c.resp.headers.__contains__('Content-Range'), False)
	eq(rc,"")

    # read byterange at start of a z length object.  should 416
    def test_13_readZObj_dlo_r0(self):
	c = makeconnection()
	oops = True
	try:
	    (rh, rc) = c.get_object(config.container2, config.myemptyobj, headers = {'Range': 'bytes=0-512'})
	except ClientException as e:
	    eq(c.c.resp.status, 416)
	    oops = False
	eq(oops,False)

    # read byterange way past start of a z length object.  should 416
    def test_14_readZObj_dlo_r1(self):
	c = makeconnection()
	oops = True
	try:
	    (rh, rc) = c.get_object(config.container2, config.myemptyobj, headers = {'Range': 'bytes=512-1024'})
	except ClientException as e:
	    eq(c.c.resp.status, 416)
	    oops = False
	eq(oops,False)

    def test_zz_end(self):
	pass
