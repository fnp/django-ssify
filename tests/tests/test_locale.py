# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

from django.conf import settings
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.utils import translation
from ssify import exceptions
from ssify.middleware import SsiMiddleware


class LocaleTestCase(TestCase):
    def setUp(self):
        self.ssi_process_response = SsiMiddleware.process_response
        SsiMiddleware.process_response = lambda self, req, res: res

    def tearDown(self):
        SsiMiddleware.process_response = self.ssi_process_response

    def test_locale_middleware(self):
        index = settings.MIDDLEWARE_CLASSES.index(
            'ssify.middleware.LocaleMiddleware')
        stock_middleware = settings.MIDDLEWARE_CLASSES[:index] + \
            ['django.middleware.locale.LocaleMiddleware'] + \
            settings.MIDDLEWARE_CLASSES[index + 1:]

        for use_stock_middleware in False, True:
            for with_lang in False, True:
                for with_i18n in False, True:
                    override = {'USE_I18N': with_i18n}

                    if use_stock_middleware:
                        override['MIDDLEWARE_CLASSES'] = stock_middleware

                    if use_stock_middleware and with_i18n:
                        expected_vary =  'Accept-Language, Cookie'
                    else:
                        expected_vary =  'Accept-Language'

                    if with_lang:
                        url = '/include_language_with_lang'
                    else:
                        url = '/include_language_without_lang'

                    with self.settings(**override):
                        # Changed USE_I18N, must reload translation mechanism.
                        translation._trans.__dict__.clear()
                        response = Client().get(url)
                        self.assertEqual(
                            response['Vary'],
                            expected_vary,
                            'Wrong Vary with: use_stock_middleware=%s, '
                            'with_lang=%s, with_i18n=%s; '
                            'expected: %s, got: %s' % (
                                use_stock_middleware, with_lang, with_i18n,
                                expected_vary, response['Vary'])
                            )

    def test_lang_arg(self):
        self.assertEqual(
            self.client.get('/language/uk').content.strip(), b'uk')
        self.assertEqual(
            self.client.get('/language').content.strip(), b'pl')

    def test_lang_arg_missing(self):
        self.assertRaises(
            exceptions.NoLangFieldError,
            lambda: self.client.get('/bad_language'))

    def test_locale_middleware_without_session(self):
        index = settings.MIDDLEWARE_CLASSES.index(
            'django.contrib.sessions.middleware.SessionMiddleware')
        middleware = settings.MIDDLEWARE_CLASSES[:index] + \
            settings.MIDDLEWARE_CLASSES[index + 1:]
        with self.settings(MIDDLEWARE_CLASSES=middleware):
            self.assertEqual(
                self.client.get('/include_language_with_lang')['Vary'],
                'Accept-Language')
            
