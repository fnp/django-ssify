#!/usr/bin/env python
# -*- coding: utf-8
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
Creates a simple Django configuration and runs tests for django-ssify.
"""
from __future__ import unicode_literals
import sys
import os
from os.path import dirname, abspath
from optparse import OptionParser

from django.conf import settings

# For convenience configure settings if they are not pre-configured or if we
# haven't been provided settings to use by environment variable.
if not settings.configured and not os.environ.get('DJANGO_SETTINGS_MODULE'):
    settings.configure(
        CACHES={
            'default': {'BACKEND':
                        'django.core.cache.backends.locmem.LocMemCache'},
            'ssify': {'BACKEND':
                      'django.core.cache.backends.locmem.LocMemCache'},
        },
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',

            'ssify',
            'tests',
        ],
        LANGUAGE_CODE='pl',
        MEDIA_URL='/media/',
        MIDDLEWARE_CLASSES=[
            'django.middleware.csrf.CsrfViewMiddleware',
            'ssify.middleware.SsiMiddleware',
            'django.middleware.cache.UpdateCacheMiddleware',
            'ssify.middleware.PrepareForCacheMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'ssify.middleware.LocaleMiddleware',
            'django.middleware.cache.FetchFromCacheMiddleware',
        ],
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        SITE_ID=1,
        TEMPLATE_CONTEXT_PROCESSORS=(
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.tz",
            "django.core.context_processors.request",
        ),
    )

try:
    from django.test.runner import DiscoverRunner
except ImportError:
    # Django < 1.6
    from django.test.simple import DjangoTestSuiteRunner as DiscoverRunner


def runtests(*test_args, **kwargs):
    """Actual test suite entry point."""
    if not test_args:
        test_args = ['tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    # For Django 1.7+
    try:
        from django import setup
    except ImportError:
        pass
    else:
        setup()

    test_runner = DiscoverRunner(
        verbosity=kwargs.get('verbosity', 1),
        interactive=kwargs.get('interactive', False),
        failfast=kwargs.get('failfast'))
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--failfast', action='store_true',
                      default=False, dest='failfast')

    (options, args) = parser.parse_args()

    runtests(failfast=options.failfast, *args)
