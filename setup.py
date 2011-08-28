#! /usr/bin/env python

from distutils.core import setup

setup(
    name = 'Masr',
    version = '0.1',
    packages=['masr',
              'masr/plugins',
              'masr/plugins/graph'],
    # Metadata
    author = 'Axel Tillequin',
    author_email = 'bdcht3@gmail.com',
    description = 'GTK/cairo canvas App framework',
    license = 'GPLv2',
    # keywords = '',
    url = 'https://github.com/bdcht/masr',
)
