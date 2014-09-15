# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

import re
import warnings
from django.test import TestCase
from django.test.utils import override_settings
from ssify.exceptions import UndeclaredSsiVarsError, UnusedSsiVarsWarning
from tests.tests_utils import split_ssi


class BasicTestCase(TestCase):
    def test_zero(self):
        self.assertEqual(
            self.client.get('/number_zero').content.strip(),
            b"<!--#set var='ve023a08d2c2075118e25b5f4339438dc' value='0'-->\n"
            b"<!--#echo var='ve023a08d2c2075118e25b5f4339438dc' "
            b"encoding='none'-->"
        )

    def test_basic_include(self):
        self.assertEqual(
            self.client.get('/basic_include').content.strip(),
            b"<!--#include file='/language/pl'-->"
        )

    def test_single_quote(self):
        self.assertEqual(
            self.client.get('/quote/3').content.strip(),
            b"""Explicit is better than implicit.
Line 3 of <!--#echo var='va50d914691ecf9b421c680d93ba1263e' encoding='none'-->
<!--#if expr='${vddc386e120ab274a980ab67384391a1a}'-->Odd number of characters.
<!--#else-->Even number of characters.
<!--#endif-->"""
        )

    def test_undeclared_vars(self):
        self.assertRaises(UndeclaredSsiVarsError,
                          self.client.get,
                          '/quote_undeclared/3')

    def test_overdeclared_vars(self):
        with warnings.catch_warnings(record=True) as w:
            response = self.client.get('/quote_overdeclared/3')
            self.assertIs(w[-1].category, UnusedSsiVarsWarning)

    def test_random_quote(self):
        self.assertEqual(
            sorted(split_ssi(self.client.get('/').content)),
            sorted([b"<!--#set var='va50d914691ecf9b421c680d93ba1263e' value='22'-->",
                 b"<!--#set var='v3e7f638af74c9f420b6d2c5fe4dda51d' value='4'-->",
                 b"<!--#set var='vafe010f2e683908fee32c48d01bb2650' value=''-->",
                 b"<!--#include file='/random_quote'-->"])
        )

        # Do it again, this time from cache.
        self.assertEqual(
            sorted(split_ssi(self.client.get('/').content)),
            sorted([b"<!--#set var='va50d914691ecf9b421c680d93ba1263e' value='22'-->",
                 b"<!--#set var='v3e7f638af74c9f420b6d2c5fe4dda51d' value='4'-->",
                 b"<!--#set var='vafe010f2e683908fee32c48d01bb2650' value=''-->",
                 b"<!--#include file='/random_quote'-->"])
        )
        self.assertEqual(
            self.client.get('/random_quote').content.strip(),
            b"<!--#include "
            b"file='/quote/${v3e7f638af74c9f420b6d2c5fe4dda51d}'-->"
        )

    @override_settings(SSIFY_RENDER=True)
    def test_debug_render_random_quote(self):
        """Renders the complete view using the SsiRenderMiddleware."""
        response = self.client.get('/')
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        self.assertEqual(
            response.content.strip(),
            b"""Simple is better than complex.
Line 4 of 22
Even number of characters."""
        )
