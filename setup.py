#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
import os
from setuptools import setup, find_packages


def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'ssify/version.py')) as f:
        variables = {}
        exec(f.read(), variables)
        return variables.get('VERSION')
    raise RuntimeError('No version info found.')


setup(
    name='django-ssify',
    version=get_version(),
    author='Radek Czajka',
    author_email='radekczajka@nowoczesnapolska.org.pl',
    url='http://git.mdrn.pl/django-ssify.git',
    packages=find_packages(exclude=['tests*']),
    package_data={'ssify': ['templates/ssify/*.html']},
    license='LICENSE',
    description='Two-phased rendering using SSI.',
    long_description=open('README.md').read(),
    install_requires=[
        'Django>=1.5',
        ],
    test_suite="runtests.runtests",
    classifiers=[
        "Development Status :: 4 - Beta",
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
    ],
    zip_safe=False,
)
