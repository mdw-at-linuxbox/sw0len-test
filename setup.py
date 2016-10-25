#!/usr/bin/python
from setuptools import setup, find_packages

setup(
	name = 'swtests',
	version = '0.0',
	description = 'test 0len radosgw/swift bug',
	packages=find_packages(),
	author='Marcus Watts',
	author_email='mwatts@redhat.com',
	install_requires = [
		"python-swiftclient",
		'PyYAML',
		'bunch >=1.0.0',
	],
)
