# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.core.urlresolvers import NoReverseMatch, reverse, resolve
from django.middleware.csrf import get_token, _sanitize_token, rotate_token
from django import template
from django.utils.translation import get_language
from ssify.decorators import ssi_variable
from ssify.utils import ssi_vary_on_cookie
from ssify.variables import SsiVariable


register = template.Library()


@register.simple_tag(takes_context=True)
def ssi_include(context, name_, **kwargs):
    """
    Inserts an SSI include statement for an URL.

    Works similarly to {% url %}, but only use keyword arguments are
    supported.

    In addition to just outputting the SSI include statement, it
    remembers any request-info the included piece declares as needed.

    """
    b_kwargs = {'lang': get_language()}
    subst = {}
    num = 0
    for k, value in kwargs.items():
        if isinstance(value, SsiVariable):
            numstr = '%04d' % num
            b_kwargs[k] = numstr
            subst[numstr] = value
            num += 1
        else:
            b_kwargs[k] = value

    try:
        url = reverse(name_, kwargs=b_kwargs)
    except NoReverseMatch:
        b_kwargs.pop('lang')
        url = reverse(name_, kwargs=b_kwargs)
    view = resolve(url).func

    for numstr, orig in subst.items():
        url = url.replace(numstr, orig.as_var())
    request = context['request']

    # Remember the SSI vars the included view says it needs.
    get_ssi_vars = getattr(view, 'get_ssi_vars', None)
    if get_ssi_vars:
        pass_vars = get_ssi_vars(**kwargs)
        for var in pass_vars:
            if not isinstance(var, SsiVariable):
                var = SsiVariable(*var)
            if not hasattr(request, 'ssi_vars_needed'):
                request.ssi_vars_needed = {}
            request.ssi_vars_needed[var.name] = var

    # Remember the decorators to use on the including view.
    patch_response = getattr(view, 'ssi_patch_response', None)
    if patch_response:
        if not hasattr(request, 'ssi_patch_response'):
            request.ssi_patch_response = []
        request.ssi_patch_response.extend(patch_response)

    # Output the SSI include.
    return "<!--#include file='%s'-->" % url


@ssi_variable(register, patch_response=[ssi_vary_on_cookie])
def get_csrf_token(request):
    """
    CsrfViewMiddleware.process_view is never called for cached
    responses, and we still need to provide a CSRF token as an
    ssi variable, we must make sure here that the CSRF token
    is in request.META['CSRF_COOKIE'].

    """
    token = get_token(request)
    if token:
        # CSRF token is already in place, just return it.
        return token

    # Mimicking CsrfViewMiddleware.process_view.
    try:
        token = _sanitize_token(request.COOKIES[settings.CSRF_COOKIE_NAME])
        request.META['CSRF_COOKIE'] = token
    except KeyError:
        # Create new CSRF token.
        rotate_token(request)
        token = get_token(request)

    return token


@register.inclusion_tag('ssify/csrf_token.html', takes_context=True)
def ssi_csrf_token(context):
    return {'request': context['request']}
