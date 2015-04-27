#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages


__requires = filter(None, open('requirements.txt').read().splitlines())

setup(
    name='vvveb',
    version='1.0.18',
    install_requires=__requires,
    description='An automatic website hosting configurator',
    author='Eugene Pankov',
    author_email='e@ajenti.org',
    url='https://github.com/ajenti/veb',
    scripts=['veb'],
    packages=find_packages(),
    include_package_data=True,
)
