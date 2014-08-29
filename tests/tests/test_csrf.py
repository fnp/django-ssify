# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

from django.conf import settings
from django.test import Client, TestCase


class CsrfTestCase(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def assertCsrfTokenOk(self, response):
        token = response.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertTrue(token)
        self.assertEqual(
            response.content.strip(),
            ("<!--#set var='vd07f6920655622adc90dd591c545bb2a' value='%s'-->\n\n"
            "<input type='hidden' name='csrfmiddlewaretoken' value='"
            "<!--#echo var='vd07f6920655622adc90dd591c545bb2a' "
            "encoding='none'-->' />" % token).encode('ascii')
        )
        return token

    def test_csrf_token(self):
        response = self.client.get('/csrf')
        token = self.assertCsrfTokenOk(response)

        # And now for a second request, with the token cookie.
        response = self.client.get('/csrf')
        new_token = self.assertCsrfTokenOk(response)
        self.assertEqual(new_token, token)

        # Make a bad request to see that CSRF protection works.
        response = self.client.post('/csrf_check', {
            'test': 'some data',
            })
        self.assertEqual(response.status_code, 403)

        # Make a good request.
        response = self.client.post('/csrf_check', {
            'test': 'some data',
            'csrfmiddlewaretoken': token,
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'some data')

    def test_new_csrf_token_in_cached_response(self):
        Client().get('/csrf')
        response = Client().get('/csrf')
        token = self.assertCsrfTokenOk(response)
