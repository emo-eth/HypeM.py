#!/usr/bin/env python

from setuptools import setup


def load_version(path):
    with open(path) as fid:
        for line in fid:
            if line.startswith('version'):
                version = line.strip().split('=')[-1][1:-1]
                return version

version = load_version('version.py')

setup(name='HypeM.py',
      py_modules=['HypeM'],
      version=version,
      description='Python 3 wrapper for the official HypeMachine API',
      author='James Wenzel',
      author_email='wenzel.james.r@gmail.com',
      url='https://github.com/jameswenzel/HypeM.py',
      download_url=('http://github.com/jameswenzel/HypeM.py/tarball'
                    '{0}'.format(version)),
      license='Apache License 2.0',
      keywords=['hypem', 'music', 'hype', 'machine', 'blogs', 'api', 'blog'],
      classifiers=[],
      install_requires=['requests >= 2.2.1', 'beautifulsoup4 >= 4.4.1']
      )
