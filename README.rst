========================
 0len cpu test
========================

This runs some simple tests to see if the 0len cpu bug
is a problem.

The tests use python-swiftclient.  On fedora,
dnf install 'python-swiftclient'.

The tests use the Nose test framework. To get started, ensure you have
the ``virtualenv`` software installed; e.g. on Debian/Ubuntu::

	sudo apt-get install python-virtualenv

and then run::

	./bootstrap

You will need to create a configuration file with the location of the
service and two different credentials, something like this::

	[func_test]
		auth_host = 10.17.152.69
		auth_port = 80
		auth_ssl = no
		auth_prefix = /auth/
		account = test
		username = tester
		email = test@nowhere.real
		display_name = Mr. Test Tester
		password = SurpriseMe!

Once you have that, you can run the tests with::

	SWIFT_TEST_CONFIG_FILE=your.conf ./virtualenv/bin/nosetests

You can specify what test(s) to run::

	SWIFT_TEST_CONFIG_FILE=your.conf ./virtualenv/bin/nosetests \
	XXX-PUT-A-TEST-NAME-HERE

Some tests have attributes set based on their current reliability and
things like AWS not enforcing their spec stricly. You can filter tests
based on their attributes::

	SWIFT_TEST_CONFIG_FILE=your.conf ./virtualenv/bin/nosetests \
	-a '!fails_on_aws'
