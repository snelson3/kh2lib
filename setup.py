import kh2lib
from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
	name = 'kh2lib',
	packages = find_packages(),
	version = 0.10,
	long_description = long_description,
	long_description_content_type='text/markdown',
	license = 'MIT',
	author = 'Thundrio',
	author_email= 'thundrio@yahoo.com',
	maintainer_email = 'thundrio@yahoo.com',
	url = 'https://github.com/snelson3/kh2lib',
	classifiers = [
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Programming Language :: Python :: 3"
	],
	platforms = 'any'
)