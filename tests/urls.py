# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns(
    'tests.views',

    # tests.basic
    url(r'^$',
        TemplateView.as_view(template_name='tests_basic/main.html')
        ),
    url(r'^number_zero$',
        TemplateView.as_view(template_name='tests_basic/number_zero.html')
        ),
    url(r'^basic_include$',
        TemplateView.as_view(template_name='tests_basic/basic_include.html')
        ),
    url(r'^random_quote$', 'random_quote', name='random_quote'),
    url(r'^quote/(?P<number>.+)$', 'quote', name='quote'),

    url(r'^quote_undeclared/(?P<number>.+)$', 'quote_undeclared'),
    url(r'^quote_overdeclared/(?P<number>.+)$', 'quote_overdeclared'),

    # tests.args
    url(r'^include_args$',
        TemplateView.as_view(template_name='tests_args/include_args.html'),
        ),
    url(r'^args$',
        TemplateView.as_view(template_name='tests_args/args.html'),
        {'limit': 3}
        ),
    url(r'^args/(?P<limit>\d+)$', 'args', name='args'),

    # tests.csrf
    url(r'^csrf$',
        TemplateView.as_view(template_name='tests_csrf/csrf_token.html'),
        ),
    url(r'^csrf_check$', 'csrf_check'),

    # tests.locale
    url(r'^include_language_with_lang$',
        TemplateView.as_view(template_name='tests_locale/include_language_with_lang.html')
        ),
    url(r'^include_language_without_lang$',
        TemplateView.as_view(template_name='tests_locale/include_language_without_lang.html')
        ),
    url(r'^language/(?P<lang>.+)$', 'language_with_lang', name='language_with_lang'),
    url(r'^language$', 'language_without_lang', name='language_without_lang'),
    url(r'^bad_language$', 'language_with_lang', name='bad_language_with_lang'),
)
