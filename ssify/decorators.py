# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
Defines decorators for use in ssify-enabled projects.
"""
from __future__ import unicode_literals
import functools
from inspect import getargspec
import warnings
from django.conf import settings
from django.http import Http404
from django.template.base import parse_bits
from django.utils.translation import get_language, activate
from .cache import cache_include, DEFAULT_TIMEOUT
from . import exceptions
from .variables import SsiVariable


def ssi_included(view=None, use_lang=True,
        timeout=DEFAULT_TIMEOUT, version=None,
        get_ssi_vars=None, patch_response=None):
    """
    Marks a view to be used as a snippet to be included with SSI.

    If use_lang is True (which is default), the URL pattern for such
    a view must provide a keyword argument named 'lang' for language.
    SSI included views don't use language or content negotiation, so
    everything they need to know has to be included in the URL.

    get_ssi_vars should be a callable which takes the view's arguments
    and returns the names of SSI variables it uses.

    """
    def dec(view):
        @functools.wraps(view)
        def new_view(request, *args, **kwargs):
            if use_lang:
                try:
                    lang = kwargs.pop('lang')
                except KeyError:
                    raise exceptions.NoLangFieldError(request)
                if lang not in [language[0] for language in settings.LANGUAGES]:
                    raise Http404
                current_lang = get_language()
                activate(lang)
                request.LANGUAGE_CODE = lang
            response = view(request, *args, **kwargs)
            if use_lang:
                activate(current_lang)
            if response.status_code == 200:
                # We don't want this view to be cached in
                # UpdateCacheMiddleware. We'll just cache the contents
                # ourselves, and point the webserver to use this cache.
                request._cache_update_cache = False

                def _check_included_vars(response):
                    used_vars = getattr(request, 'ssi_vars_needed', {})
                    if get_ssi_vars:
                        # Remove the ssi vars that should be provided
                        # by the including view.
                        pass_vars = get_ssi_vars(*args, **kwargs)

                        for var in pass_vars:
                            if not isinstance(var, SsiVariable):
                                var = SsiVariable(*var)
                            try:
                                del used_vars[var.name]
                            except KeyError:
                                warnings.warn(
                                    exceptions.UnusedSsiVarsWarning(
                                        request, var))
                    if used_vars:
                        raise exceptions.UndeclaredSsiVarsError(
                            request, used_vars)
                    request.ssi_vars_needed = {}

                    # Don't use default django response caching for this view,
                    # just save the contents instead.
                    cache_include(request.path, response.content,
                        timeout=timeout, version=version)

                if hasattr(response, 'render') and callable(response.render):
                    response.add_post_render_callback(_check_included_vars)
                else:
                    _check_included_vars(response)

            return response

        # Remember get_ssi_vars so that in can be computed from args/kwargs
        # by including view.
        new_view.get_ssi_vars = get_ssi_vars
        new_view.ssi_patch_response = patch_response
        return new_view
    return dec(view) if view else dec


def ssi_variable(register, name=None, patch_response=None):
    """
    Creates a template tag representing an SSI variable from a function.

    The function must take 'request' as its first argument.
    It may take other arguments, which should be provided when using
    the template tag.

    """
    # Cache control?
    def dec(func):

        # Find own path.
        function_name = (name or
                         getattr(func, '_decorated_function', func).__name__)
        lib_name = func.__module__.rsplit('.', 1)[-1]
        tagpath = "%s.%s" % (lib_name, function_name)
        # Make sure the function takes request parameter.
        params, varargs, varkw, defaults = getargspec(func)
        assert params and params[0] == 'request', '%s is decorated with '\
            'request_info_tag, so it must take `request` for '\
            'its first argument.' % (tagpath)

        @register.tag(name=function_name)
        def _ssi_var_tag(parser, token):
            """
            Creates a SSI variable reference for a request-dependent info.

            Use as:
                {% ri_tag args... %}
            or:
                {% ri_tag args... as variable %}
                {{ variable.if }}
                    {{ variable }}, or
                    {% ssi_include 'some-snippet' variable %}
                {{ variable.else }}
                    Default text
                {{ variable.endif }}

            """
            bits = token.split_contents()[1:]

            # Is it the 'as' form?
            if len(bits) >= 2 and bits[-2] == 'as':
                asvar = bits[-1]
                bits = bits[:-2]
            else:
                asvar = None

            # Parse the arguments like Django's generic tags do.
            args, kwargs = parse_bits(parser, bits,
                                      ['context'] + params[1:], varargs, varkw,
                                      defaults, takes_context=True,
                                      name=function_name)
            return SsiVariableNode(tagpath, args, kwargs, patch_response, asvar)
        _ssi_var_tag.get_value = func
        #return _ssi_var_tag
        return func

    return dec


from .variables import SsiVariableNode
