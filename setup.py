# pylint: disable=no-member, no-name-in-module, import-error

from __future__ import absolute_import
import glob
import os
import distutils.command.sdist
import distutils.log
import subprocess
from setuptools import Command, setup
import setuptools.command.sdist

# Patch setuptools' sdist behaviour with distutils' sdist behaviour
setuptools.command.sdist.sdist.run = distutils.command.sdist.sdist.run

VERSION_INFO = {}
CWD = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(CWD, "dxltieclient", "_version.py")) as f:
    exec(f.read(), VERSION_INFO)  # pylint: disable=exec-used


class LintCommand(Command):
    """
    Custom setuptools command for running lint
    """
    description = 'run lint against project source files'
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.announce("Running pylint for library source files and tests",
                      level=distutils.log.INFO)
        subprocess.check_call(["pylint", "dxltieclient"] + glob.glob("*.py"))


class CiCommand(Command):
    """
    Custom setuptools command for running steps that are performed during
    Continuous Integration testing.
    """
    description = 'run CI steps (lint, test, etc.)'
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.run_command("lint")

TEST_REQUIREMENTS = ["pylint"]

DEV_REQUIREMENTS = TEST_REQUIREMENTS + ["sphinx"]

setup(
    # Application name:
    name="dxltieclient",

    # Version number:
    version=VERSION_INFO["__version__"],

    # Requirements
    install_requires=[
        "dxlbootstrap>=0.1.3",
        "dxlclient"
    ],

    tests_require=TEST_REQUIREMENTS,

    extras_require={
        "dev": DEV_REQUIREMENTS,
        "test": TEST_REQUIREMENTS
    },

    # Application author details:
    author="McAfee, Inc.",

    # License
    license="Apache License 2.0",

    keywords=['opendxl', 'dxl', 'mcafee', 'client', 'tie'],

    # Packages
    packages=[
        "dxltieclient",
        "dxltieclient._config",
        "dxltieclient._config.sample"
    ],

    package_data={
        "dxltieclient._config.sample" : ['*']},

    # Details
    url="http://www.mcafee.com/",

    description="McAfee Threat Intelligence Exchange (TIE) DXL client library",

    long_description=open('README').read(),

    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6"
    ],

    cmdclass={
        'ci': CiCommand,
        'lint': LintCommand
    }
)
