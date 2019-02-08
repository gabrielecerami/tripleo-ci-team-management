#!/usr/bin/env python

from setuptools import setup

setup(name='Tripleo CI Taiga Management tool',
      version='0.1',
      author='Gabriele Cerami',
      author_email='gcerami@redhat.com',
      packages=['taigacli', 'taigacli_custom_queries'],
      install_requires=[
          'pandas',
          'texttable',
          'python-taiga',
          'graphviz',
          'sqlalchemy',
          'sqlalchemy_utils',
      ],
      entry_points={
          'console_scripts': [
              'taigacli=taigacli.taigacli:main',
          ],
      },
      )
