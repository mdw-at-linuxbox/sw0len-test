import swiftclient.client
from bunch import *
from ConfigParser import SafeConfigParser as sc
import ConfigParser
from os import environ
import re

swift = Bunch()
config = Bunch()

# apparently, see https://bugs.launchpad.net/swift/+bug/820185.
import logging
logging.raiseExceptions = False

## XXX fixme
auth = environ.get('ST_AUTH')
auth_version = environ.get('ST_AUTH_VERSION', '1.0')
user = environ.get('ST_USER')
key = environ.get('ST_KEY')

container = "container"
myobj = "myobj"
mynewobj = "mynewobj"
myemptyobj = "myemptyobj"

myconn = {}
class TestConnection():
    def __init__(self, _u, _t, _p, _c):
	self.url = _u
	self.token = _t
	self.parsed = _p
	self.c = _c
    def put_container(self, container):
	e = swiftclient.client.put_container(self.url, self.token, container, http_conn = (self.parsed, self.c))
	return e
    def delete_container(self, container):
	e = swiftclient.client.delete_container(self.url, self.token, container, http_conn = (self.parsed, self.c))
	return e
    def put_object(self, container, object, contents = None, headers = None):
	e = swiftclient.client.put_object(self.url, self.token, container, object, contents, headers = headers, http_conn = (self.parsed, self.c))
	return e
    def get_object(self, container, object, headers = None):
	(rh,rc) = swiftclient.client.get_object(self.url, self.token, container, object, headers = headers, http_conn = (self.parsed, self.c))
	return (rh,rc)
    def delete_object(self, container, object):
	e = swiftclient.client.delete_object(self.url, self.token, container, object, http_conn = (self.parsed, self.c))
	return e

def get_auth(c):
    auth = 'https' if c.func_test.auth_ssl == "yes" else 'http'
    auth += '://'
    auth += c.func_test.auth_host
    auth += c.func_test.auth_prefix
    auth += "1.0"
    return auth

def get_user(c):
    user = c.func_test.account
    user += ':'
    user += c.func_test.username
    return user

def makeconnection():
    global myconn, config
    auth = get_auth(config)
    user = get_user(config)
    key = config.func_test.password
    if myconn.has_key(auth):
	return myconn[auth]
    url, token = swiftclient.client.get_auth(auth, user, key,
     auth_version=auth_version)

    parsed, c = swiftclient.client.http_connection(url)
    x = TestConnection(url, token, parsed, c)
    myconn[auth] = x
    return x

def read_config(fp, defaults=None):
    x = {}
    if defaults is None:
	defaults = {}
    c = sc(defaults)
    if hasattr(fp, 'readline'):
	c.readfp(fp)
    else:
	if not c.read(conffile):
	    sys.stderr.write("cannot read config file %s\n" % conffile)
	    sys.exit(1)
    for s in c.sections():
	x.update({s: Bunch.fromDict(dict(c.items(s)))})
    x['__file__'] = str(fp)
    return x

## nosetests runs this automagically
def setup():
    global swift, config
    swift.clear()
    config.clear()
    d = {}

    auth = environ.get('ST_AUTH')
    auth_version = environ.get('ST_AUTH_VERSION', '1.0')
    user = environ.get('ST_USER')
    key = environ.get('ST_KEY')
    # what about version ???
    if auth is not None:
	m = re.match("([a-z]*)://([^/]*):([^/]*)(/.*/)([^/]*)$")
	if m:
	    d.func_test.auth_ssl = "yes" if match(1) == 'https' else "no"
	    d.func_test.auth_host = match(2)
	    d.func_test.auth_port = match(3)
	    d.func_test.auth_auth = match(4)
	else:
	    m = re.match("([a-z]*)://([^/]*)(/.*/)([^/]*)$")
	    if m:
		d.func_test.auth_ssl = "yes" if match(1) == 'https' else "no"
		d.func_test.auth_host = match(2)
		d.func_test.auth_port = '443' if d.func_test_auth_ssl == "yes" else '80'
		d.func_test.auth_auth = match(3)
	    else:
		raise ValueError("dont understand ST_AUTH %s" % auth)
    if user is not None:
	m = re.match("(.*):(.*)")
	if m:
	    d.func_test.account = match(1)
	    d.func_test.username = match(2)
	else:
	    raise ValueError("dont understand ST_USER %s" % user)
    config_file = environ.get('SWIFT_TEST_CONFIG_FILE',
	'/etc/swift/func_test.conf')
    with file(config_file) as f:
	config.update(read_config(f, d))

## nosetests runs this automagically
def teardown():
    pass

