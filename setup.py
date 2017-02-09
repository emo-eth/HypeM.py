#!/usr/bin/env python

from setuptools import setup

version = '1.1.0'

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
      install_requires=['beautifulsoup4 >= 4.4.1', 'baseapi >= 0.1.0']
      )
