import swiftclient.client
import bunch
import yaml
from os import environ

swift = bunch.Bunch()
config = bunch.Bunch()

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

def read_config(fp):
    config = bunch.Bunch()
    g = yaml.safe_load_all(fp)
    for new in g:
	config.update(bunch.bunchify(new))
    return config

## nosetests runs this automagically
def setup():
    global swift, config
    swift.clear()
    config.clear()

    config_file = environ.get('SWIFT_TEST_CONFIG_FILE',
	'/etc/swift/func_test.conf')
    with file(config_file) as f:
	config.update(read_config(f))

## nosetests runs this automagically
def teardown():
    pass

def makeconnection():
    global myconn
    auth = environ.get('SWIFTTEST_CONF')
    auth_version = environ.get('ST_AUTH_VERSION', '1.0')
    user = environ.get('ST_USER')
    key = environ.get('ST_KEY')
    x = myconn[auth]
    if x:
	return x
    url, token = swiftclient.client.get_auth(auth, user, key,
     auth_version=auth_version)

    parsed, c = swiftclient.client.http_connection(url)
    x = {'url': url, 'token': token, 'parsed': parsed, 'conn': c}
    myconn[auth] = x
    return x
