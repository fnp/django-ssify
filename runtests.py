#!/usr/bin/env python
import sys
import os
from os.path import dirname, abspath
from optparse import OptionParser

from django.conf import settings, global_settings

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
        MEDIA_URL='/media/',
        MIDDLEWARE_CLASSES=[
            'ssify.middleware.SsiMiddleware',
            'django.middleware.cache.UpdateCacheMiddleware',
            'ssify.middleware.PrepareForCacheMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.cache.FetchFromCacheMiddleware',
        ],
        STATIC_URL='/static/',
        ROOT_URLCONF='tests.urls',
        SITE_ID=1,
        SSIFY_DEBUG_VERBOSE=False,
        TEMPLATE_CONTEXT_PROCESSORS=(
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.tz",
            "django.core.context_processors.request",
        ),
    )

from django.test.simple import DjangoTestSuiteRunner


def runtests(*test_args, **kwargs):
    if 'south' in settings.INSTALLED_APPS:
        from south.management.commands import patch_for_test_db_setup
        patch_for_test_db_setup()

    if not test_args:
        test_args = ['tests']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    test_runner = DjangoTestSuiteRunner(
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
