#!/usr/bin/env python

import sys
import os
from setuptools import setup


long_description='''\
Xigt is a framemwork for working with interlinear glossed text (IGT). It
provides a data model and XML format as well as an API for
programmatically interacting with Xigt data. The format has a flat
structure and makes use of IDs and references to encode the annotation
structure of an IGT. This architecture allows for interesting extensions
to the standard IGT tiers, such as for parse trees, dependencies,
bilingual alignments, and more.'''

base_dir = os.path.dirname(__file__)
about = {}
with open(os.path.join(base_dir, "xigt", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=long_description,
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic'
    ],
    keywords='nlp igt linguistics',
    packages=[
        'xigt',
        'xigt.codecs',
        'xigt.importers',
        'xigt.exporters',
        'xigt.scripts'
    ],
    extras_require={
        'dev': ['pytest'],
        # 'toolbox': ['toolbox'],
        # 'itsdb': ['pydelphin']
        # 'odin': ['odin-utils']
    },
    entry_points={
        'console_scripts': [
            'xigt=xigt.main:main'
        ]
    },
)
