# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

import re
from django.test import TestCase
from django.test.utils import override_settings
from tests.tests_utils import split_ssi


class ArgsTestCase(TestCase):
    def test_args(self):
        self.assertEqual(
            sorted(split_ssi(self.client.get('/args').content)),
            sorted([b"<!--#set var='vff80027f1d552d08d46c8b603948d85c' value='2'-->",
                 b"<!--#set var='veeb5ec4364971b409c48e36bd1428d03' value='1'-->",
                 b"<!--#set var='v05a1f9ec205c5aa84197f6b326c518a2' value='0'-->",
                 b"<!--#echo var='v05a1f9ec205c5aa84197f6b326c518a2' encoding='none'-->",
                 ])
            )

    def test_args_included(self):
        self.assertEqual(
            self.client.get('/args/3').content.strip(),
            b"<!--#echo var='v05a1f9ec205c5aa84197f6b326c518a2' encoding='none'-->"
            )

    def test_include_args(self):
        self.assertEqual(
            sorted(split_ssi(self.client.get('/include_args').content)),
            sorted([b"<!--#set var='vf6aba0780227af845107c046f336cc8a' value='3'-->",
                 b"<!--#set var='vff80027f1d552d08d46c8b603948d85c' value='2'-->",
                 b"<!--#set var='veeb5ec4364971b409c48e36bd1428d03' value='1'-->",
                 b"<!--#set var='v05a1f9ec205c5aa84197f6b326c518a2' value='0'-->",
                 b"<!--#include file='/args/${vf6aba0780227af845107c046f336cc8a}'-->",
                 ]),
            )

        # Test a second time, this time from cache.
        self.assertEqual(
            sorted(split_ssi(self.client.get('/include_args').content)),
            sorted([b"<!--#set var='vf6aba0780227af845107c046f336cc8a' value='3'-->",
                 b"<!--#set var='vff80027f1d552d08d46c8b603948d85c' value='2'-->",
                 b"<!--#set var='veeb5ec4364971b409c48e36bd1428d03' value='1'-->",
                 b"<!--#set var='v05a1f9ec205c5aa84197f6b326c518a2' value='0'-->",
                 b"<!--#include file='/args/${vf6aba0780227af845107c046f336cc8a}'-->",
                 ]),
            )

    @override_settings(SSIFY_RENDER=True)
    def test_render_include_args(self):
        """Renders the complete view using the SsiRenderMiddleware."""
        response = self.client.get('/include_args')
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        self.assertEqual(
            response.content.strip(),
            b"""0"""
        )
