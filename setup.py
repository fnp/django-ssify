#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from setuptools import setup, find_packages

setup(
    name='django-ssify',
    version='0.1',
    author='Radek Czajka',
    author_email='radekczajka@nowoczesnapolska.org.pl',
    url='',
    packages=find_packages(exclude=['tests*']),
    license='LICENSE',
    description='Two-phased rendering using SSI.',
    long_description=open('README.md').read(),
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Code Generators",
    ]
)
