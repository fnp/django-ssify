# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings


@override_settings(SSIFY_RENDER=True)
class RenderTestCase(TestCase):
    def test_render(self):
        """Renders the complete view using the SsiRenderMiddleware."""
        response = self.client.get('/render')
        if hasattr(response, 'render') and callable(response.render):
            response.render()
        self.assertEqual(
            response.content.decode('utf-8').strip(),
            """Zażółć gęślą jaźń\n'"\\ <!--#echo var='test' encoding='none'-->"""
        )
