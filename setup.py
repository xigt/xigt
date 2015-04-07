#!/usr/bin/env python3

from setuptools import setup

long_description='''\
Xigt is a framemwork for working with interlinear glossed text (IGT). It
provides a data model and XML format as well as an API for
programmatically interacting with Xigt data. The format has a flat
structure and makes use of IDs and references to encode the annotation
structure of an IGT. This architecture allows for interesting extensions
to the standard IGT tiers, such as for parse trees, dependencies,
bilingual alignments, and more.'''

setup(
    name='Xigt',
    version='1.0rc1',
    description='A framework for eXtensible Interlinear Glossed Text',
    long_description=long_description,
    url='https://github.com/goodmami/xigt',
    author='Michael Wayne Goodman',
    author_email='goodman.m.w@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
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
    #extras_require={
    #    'toolbox': ['toolbox'],
    #    'itsdb': ['pydelphin']
    #}
    entry_points={
        'console_scripts': [
            'xigt=xigt.main:main'
        ]
    },
    test_suite='tests'
)
