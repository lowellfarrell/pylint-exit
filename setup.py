#!/usr/bin/python
from setuptools import setup

setup(
    name='pylint-exit-options',
    description='Exit code handler for pylint command line utility.',
    version='2.0.0',
    author='Lowell-Farrell',
    author_email='lff.dev19@gmail.com',
    py_modules=['pylint_exit_options'],
    setup_requires=['setuptools', 'wheel', 'm2r'],
    tests_require=[],
    install_requires=['bitarray', 'pylint'],
    data_files=[],
    options={
        'bdist_wheel': {'universal': True}
    },
    url='https://github.com/lowellfarrell/pylint-exit-options',
    entry_points={
        'console_scripts': ['pylint-exit-options=pylint_exit_opitons:main'],
    }
)
