# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import unicode_literals

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import translation
from ssify import ssi_included, ssi_expect, SsiVariable as V


@ssi_included(use_lang=False, get_ssi_vars=lambda number: [
    ('test_tags.number_of_quotes',),
    ('test_tags.quote_len_odd', [ssi_expect(number, int)])
])
def quote(request, number):
    number = int(number)
    return render(request, 'tests_basic/quote.html', {
        'number': number,
        'quote': QUOTES[number]
    })


@ssi_included(use_lang=False)
def quote_undeclared(request, number):
    number = int(number)
    return render(request, 'tests_basic/quote.html', {
        'number': number,
        'quote': QUOTES[number]
    })


@ssi_included(use_lang=False, get_ssi_vars=lambda number: [
    ('test_tags.number_of_quotes',),
    ('test_tags.quote_len_odd', [ssi_expect(number, int)]),
    ('test_tags.quote_len_odd', [V('nonexistent')]),
])
def quote_overdeclared(request, number):
    number = int(number)
    return render(request, 'tests_basic/quote.html', {
        'number': number,
        'quote': QUOTES[number]
    })



@ssi_included(use_lang=False, get_ssi_vars=lambda: (
    lambda number: [number] + quote.get_ssi_vars(number))(
        number=V('test_tags.random_number', (), {'limit': V('test_tags.number_of_quotes')})
    ))
def random_quote(request):
    """
    This view is purposely overcomplicated to test interdependencies
    between SSI variables and SSI includes.

    It finds number of quotes and sets that in an SSI variable,
    then uses that to set a random quote number in a second variable,
    then sets a third saying if the length of the selected quote is odd.

    """
    return render(request, 'tests_basic/random_quote.html')


def language(request):
    assert request.LANGUAGE_CODE == translation.get_language()
    return HttpResponse(request.LANGUAGE_CODE)

language_without_lang = ssi_included(use_lang=False)(language)
language_with_lang = ssi_included(language)




@ssi_included(use_lang=False, get_ssi_vars=lambda limit: (
    ('test_tags.random_number', [], {'limit': ssi_expect(limit, int)}),
    ('test_tags.random_number', [V(
        'test_tags.random_number', [], {'limit': ssi_expect(limit, int)}
    )]),
    ('test_tags.random_number', [], {'limit': V(
        'test_tags.random_number', [V(
            'test_tags.random_number', [], {'limit': ssi_expect(limit, int)}
        )]
    )}),
    ))
def args(request, limit):
    return render(request, 'tests_args/args.html', {'limit': int(limit)})


def csrf_check(request):
    return HttpResponse(request.POST['test'])


# Nothing interesting here.
def _quotes():
    import sys
    stdout_backup = sys.stdout
    try:
        # Python 2
        from cStringIO import StringIO
        sys.stdout = StringIO()
    except ImportError:
        # Python 3
        from io import BytesIO, TextIOWrapper
        sys.stdout = TextIOWrapper(BytesIO(), sys.stdout.encoding)
    import this
    sys.stdout.seek(0)
    this_string = sys.stdout.read()
    sys.stdout.close()
    sys.stdout = stdout_backup
    return this_string.split('\n')

QUOTES = _quotes()
