mport swiftclient.client
from os import environ

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

def makeconnection():
    global myconn
    x = myconn[auth]
    if x:
	return x
    url, token = swiftclient.client.get_auth(auth, user, key,
     auth_version=auth_version)

    parsed, c = swiftclient.client.http_connection(url)
    x = {'url': url, 'token': token, 'parsed': parsed, 'conn': c}
    myconn[auth] = x
    return x

def test_foo:
    print "hi there"
