#!/usr/bin/env python

from setuptools import setup

setup(name='Tripleo CI Taiga Management tool',
      version='0.1',
      author='Gabriele Cerami',
      author_email='gcerami@redhat.com',
      packages=['taigacli'],
      install_requires=[
          'pandas',
          'texttable',
          'python-taiga',
      ],
      entry_points={
          'console_scripts': [
              'taigacli=taigacli.taigacli:main',
          ],
      },
     )
