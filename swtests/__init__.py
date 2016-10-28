import swiftclient.client
from bunch import *
from ConfigParser import SafeConfigParser as sc
from swiftclient.exceptions import ClientException
import ConfigParser
from os import environ
import json
import re
import sys

swift = Bunch()
config = Bunch()

# apparently, see https://bugs.launchpad.net/swift/+bug/820185.
import logging
logging.raiseExceptions = False

## XXX fixme
#auth = environ.get('ST_AUTH')
#auth_version = environ.get('ST_AUTH_VERSION', '1.0')
#user = environ.get('ST_USER')

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
    def get_container(self, container, headers = None):
	(rh,rc) = swiftclient.client.get_container(self.url, self.token, container, headers = headers, http_conn = (self.parsed, self.c))
	return (rh,rc)
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
     auth_version=config.func_test.auth_version)

    parsed, c = swiftclient.client.http_connection(url, timeout=15)
    x = TestConnection(url, token, parsed, c)
    myconn[auth] = x
    return x

def flush_connection():
    auth = get_auth(config)
    try:
	myconn.pop(auth)
    except:
	pass

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

def readin_configuration():
    global swift, config
    mark = 0
    swift.clear()
    config.clear()
    d = {}
    d['container1'] = 'box'
    d['container2'] = 'container'
    d['myobj'] = 'myobj'
    d['mynewobj'] = 'mynewobj'
    d['myemptyobj'] = 'myemptyobj'
    func_test = {}

    auth = environ.get('ST_AUTH')
    auth_version = environ.get('ST_AUTH_VERSION', '1.0')
    user = environ.get('ST_USER')
    key = environ.get('ST_KEY')
    func_test['password'] = key
    func_test['auth_version'] = auth_version
    # what about version ???
    if auth is not None:
	m = re.match("([a-z]*)://([^/]*):([^/]*)(/.*/)([^/]*)$", auth)
	if m:
	    mark |= 1
	    func_test['auth_ssl'] = "yes" if m.group(1) == 'https' else "no"
	    func_test['auth_host'] = m.group(2)
	    func_test['auth_port'] = m.group(3)
	    func_test['auth_prefix'] = m.group(4)
	    func_test['auth_version'] = m.group(5)
	else:
	    m = re.match("([a-z]*)://([^/]*)(/.*/)([^/]*)$", auth)
	    if m:
		mark |= 1
		func_test['auth_ssl'] = "yes" if m.group(1) == 'https' else "no"
		func_test['auth_host'] = m.group(2)
		func_test['auth_port'] = '443' if func_test['auth_ssl'] == "yes" else '80'
		func_test['auth_prefix'] = m.group(3)
		func_test['auth_version'] = m.group(4)
	    else:
		raise ValueError("dont understand ST_AUTH %s" % auth)
    if user is not None:
	m = re.match("(.*):(.*)", user)
	if m:
	    mark |=2
	    func_test['account'] = m.group(1)
	    func_test['username'] = m.group(2)
	else:
	    raise ValueError("dont understand ST_USER %s" % user)
    config_file = environ.get('SWIFT_TEST_CONFIG_FILE',
	'/etc/swift/func_test.conf')
    d['func_test'] = func_test
    try:
	with file(config_file) as f:
	    config.update(read_config(f))
    except IOError, i:
	e = sys.exc_info()[0]
	if mark != 3:
	    sys.stderr.write("warning: can't reading config file '%s': %s\n" % (f, e))
    if not config.get('func_test'):
	config['func_test'] = Bunch()
    for j in func_test:
	if not config.get('func_test').get(j):
	    config['func_test'][j] = func_test[j]
    for j in d:
	if not config.get(j):
	    config[j] = d[j]

def make_containers_and_objects():
    c = makeconnection()
    for j in [config.container2]:
	e = c.put_container(j)
    e = c.put_object(config.container2, config.myobj + "/00000001", "a short bit of text")
    e = c.put_object(config.container2, config.myobj + "/00000002")
    e = c.put_object(config.container2, config.myobj,
	headers={'X-Object-Manifest': config.container2 + "/" + config.myobj + "/"})
    e = c.put_object(config.container2, config.mynewobj + "/00000001", "a short bit of text")
    e = c.put_object(config.container2, config.mynewobj + "/00000002")
    e = c.put_object(config.container2, config.mynewobj + "/00000003", "and another short piece of text")
    e = c.put_object(config.container2, config.mynewobj,
	headers={'X-Object-Manifest': config.container2 + "/" + config.mynewobj + "/"})
    e = c.put_object(config.container2, config.myemptyobj + "/00000001")
    e = c.put_object(config.container2, config.myemptyobj,
	headers={'X-Object-Manifest': config.container2 + "/" + config.myemptyobj + "/"})

def do_cleanup():
    no_cleanup = environ.get('ST_NO_CLEANUP')
    if no_cleanup:
	return
    c = makeconnection()
    to_delete_containers = {}
    for j in [config.container1, config.container2]:
	to_delete = []
	mark = False
	rc = []
	try:
	    (rh,rc) = c.get_container(j)
	    mark = True
	except ClientException:
	    pass
	except:
	    e = sys.exc_info()[0]
	    sys.stderr.write("error listing '%s': %s\n" % (j, e))
	rc.sort(key=lambda x: x['name'], reverse=True)
	if mark:
	    for o in rc:
		to_delete.append(o['name'])
	    to_delete_containers[j] = to_delete
#    if not to_delete_containers:
#	sys.stderr.write("nothing to delete!\n")
    for j in to_delete_containers.keys():
	for o in to_delete_containers[j]:
	    try:
		e = c.delete_object(j, o)
	    except ClientException:
		pass
	    except:
		e = sys.exc_info()[0]
		sys.stderr.write("error deleting object '%s/%s': %s\n" % (j, o, e))
	try:
	    c.delete_container(j)
	except ClientException:
	    pass
	except:
	    e = sys.exc_info()[0]
	    sys.stderr.write("error deleting container '%s': %s\n" % (j, e))

## nosetests runs this automagically
def setup():
#    sys.stderr.write("setup\n")
    readin_configuration()
    do_cleanup()
    make_containers_and_objects()

## nosetests runs this automagically
def teardown():
    do_cleanup()
    pass
