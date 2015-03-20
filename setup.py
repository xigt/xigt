#!/usr/bin/env python3

from unittest import TextTestRunner, TestLoader
from glob import glob
from os.path import splitext, basename, join as pjoin
import os
from distutils.core import setup, Command

# thanks: http://da44en.wordpress.com/2002/11/22/using-distutils/
class TestCommand(Command):
    description='run unit tests'
    user_options = [ ]

    def initialize_options(self):
        self._dir = os.getcwd()

    def finalize_options(self):
        pass

    def run(self):
        '''
        Finds all the tests modules in tests/, and runs them.
        '''
        testfiles = [ ]
        for t in glob(pjoin(self._dir, 'tests', '*.py')):
            if not t.endswith('__init__.py'):
                testfiles.append('.'.join(
                    ['tests', splitext(basename(t))[0]])
                )

        tests = TestLoader().loadTestsFromNames(testfiles)
        t = TextTestRunner(verbosity = 1)
        t.run(tests)

setup(
	name='Xigt',
    version='0.1',
    url='https://github.com/goodmami/xigt',
	author='Michael Wayne Goodman',
	author_email='goodman.m.w@gmail.com',
	description='A library and schema for eXtensible Interlinear Glossed Text',
	packages=['xigt','xigt.codecs'],
    scripts=[
        'bin/xigt-import',
        'bin/xigt-export',
        'bin/xigt-process',
        'bin/xigt-query',
        'bin/xigt-validate'
    ],
	cmdclass={'test':TestCommand}
)
