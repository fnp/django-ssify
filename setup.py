#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from setuptools import setup, find_packages

setup(
    name='django-ssify',
    version='0.1',
    author='Radek Czajka',
    author_email='radekczajka@nowoczesnapolska.org.pl',
    url='http://git.nowoczesnapolska.org.pl/?p=django-ssify.git',
    packages=find_packages(exclude=['tests*']),
    license='LICENSE',
    description='Two-phased rendering using SSI.',
    long_description=open('README.md').read(),
    install_requires=[
        'Django>=1.4',
        ],
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Code Generators",
    ]
)
