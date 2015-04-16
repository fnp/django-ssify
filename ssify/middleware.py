# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
Middleware classes provide by django-ssify.

The main middleware you should use is SsiMiddleware. It's responsible
for providing the SSI variables needed for the SSI part of rendering.

If you're using django's UpdateCacheMiddleware, add
PrepareForCacheMiddleware *after it* also. It will add all the data
needed by SsiMiddleware to the response.

If you're using SessionMiddleware with LocaleMiddleware and your
USE_I18N or USE_L10N is True, you should also use the provided
LocaleMiddleware instead of the stock one.

And, last but not least, if using CsrfViewMiddleware, move it to the
top of MIDDLEWARE_CLASSES, even before SsiMiddleware, and use
`csrf_token` from `ssify` tags library in your templates, this way
your CSRF tokens will be set correctly.

So, you should end up with something like this:

    MIDDLEWARE_CLASSES = [
       'django.middleware.csrf.CsrfViewMiddleware',
       'ssify.middleware.SsiMiddleware',
       'django.middleware.cache.UpdateCacheMiddleware',
       'ssify.middleware.PrepareForCacheMiddleware',
       ...
       'ssify.middleware.LocaleMiddleware',
       ...
    ]


"""
from __future__ import unicode_literals
from django.conf import settings
from django.middleware import locale
from django.utils.cache import patch_vary_headers
from .conf import conf
from .serializers import json_decode, json_encode
from .utils import ssi_vary_on_cookie
from .variables import SsiVariable, provide_vars


CACHE_HEADERS = ('Pragma', 'Cache-Control', 'Vary')


class PrepareForCacheMiddleware(object):
    """
    Patches the response object with all the data SsiMiddleware needs.

    This should go after UpdateCacheMiddleware in MIDDLEWARE_CLASSES.
    """
    @staticmethod
    def process_response(request, response):
        """Adds a 'X-Ssi-Vars-Needed' header to the response."""
        if ('X-Ssi-Vars-Needed' not in response and
                getattr(request, 'ssi_vars_needed', None)):
            vars_needed = {}
            for (k, v) in request.ssi_vars_needed.items():
                vars_needed[k] = v.definition
            response['X-Ssi-Vars-Needed'] = json_encode(
                vars_needed, sort_keys=True)

        if ('X-ssi-restore' not in response and
                getattr(request, 'ssi_patch_response', None)):
            # We have some response modifiers set by ssi_includes and
            # ssi_variables. Those are used, because unrendered SSI
            # templates Django cache receives should have different
            # caching headers, than pages rendered with request-specific
            # information.
            # What we do here is apply the modifiers, but restore
            # previous values of any cache-relevant headers and set
            # a custom header with modified values to set them
            # after-cache.
            original_fields = {}
            for field in CACHE_HEADERS:
                original_fields[field] = response.get(field, None)
            for modifier in request.ssi_patch_response:
                modifier(response)
            restore_fields = {}
            for field in CACHE_HEADERS:
                new_value = response.get(field, None)
                if new_value != original_fields[field]:
                    restore_fields[field] = new_value
                    if original_fields[field] is None:
                        del response[field]
                    else:
                        response[field] = original_fields[field]
            response['X-ssi-restore'] = json_encode(restore_fields)

        return response


class SsiMiddleware(object):
    """
    The main django-ssify middleware.

    It prepends the response content with SSI set statements,
    providing values for any SSI variables used in the templates.

    It also patches the Vary header with the values given by
    the SSI variables.

    If SSIFY_RENDER is set, it also passes the response through
    SsiRenderMiddleware, which interprets and renders the SSI
    statements, so you can see the output without an actual
    SSI-enabled webserver.

    """
    def process_request(self, request):
        request.ssi_patch_response = []

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.ssi_vars_needed = {}

    def _process_rendered_response(self, request, response):
        # Prepend the SSI variables.
        if hasattr(request, 'ssi_vars_needed'):
            vars_needed = request.ssi_vars_needed
        elif 'X-Ssi-Vars-Needed' in response:
            vars_needed = json_decode(response['X-Ssi-Vars-Needed'])
            for k, v in vars_needed.items():
                vars_needed[k] = SsiVariable(*v)
            if not settings.DEBUG:
                del response['X-Ssi-Vars-Needed']
        else:
            vars_needed = None

        if vars_needed:
            response.content = provide_vars(request, vars_needed) + \
                response.content

        if 'X-ssi-restore' in response:
            # The modifiers have already been applied to the response
            # by the PrepareForCacheMiddleware.
            # All we need to do is restore cache-relevant headers.
            for header, content in json_decode(response['X-ssi-restore']).items():
                if content is None:
                    del response[header]
                else:
                    response[header] = content
            if not settings.DEBUG:
                del response['X-ssi-restore']
        else:
            for response_modifier in getattr(request, 'ssi_patch_response', []):
                response_modifier(response)

    def process_response(self, request, response):
        if hasattr(response, 'render') and callable(response.render):
            response.add_post_render_callback(
                lambda r: self._process_rendered_response(request, r)
            )
        else:
            self._process_rendered_response(request, response)

        if conf.RENDER:
            from .middleware_debug import SsiRenderMiddleware
            response = SsiRenderMiddleware().process_response(
                request, response)

        return response


class LocaleMiddleware(locale.LocaleMiddleware):
    """
    Version of the LocaleMiddleware for use together with the
    SsiMiddleware if USE_I18N or USE_L10N is set.

    Stock LocaleMiddleware looks for user language selection in
    the session data and cookies, before it falls back to parsing
    Accept-Language. The effect of accessing the session is adding
    the `Vary: Cookie` header to the response.  While this is correct
    behaviour, it renders the cache system useless (see
    https://code.djangoproject.com/ticket/13217).

    This version of LocaleMiddleware doesn't mark the session
    as accessed on every request, so SessionMiddleware doesn't add the
    Vary: Cookie header (unless something else actually uses the session
    in a meaningful way, of course). Instead, it tells SsiMiddleware
    to add the Vary: Cookie header to the final response.

    """
    def process_request(self, request):
        if hasattr(request, 'session'):
            session_accessed_before = request.session.accessed
        else:
            session_accessed_before = None
        super(LocaleMiddleware, self).process_request(request)
        if session_accessed_before is False:
            if (request.session.accessed and
                    (settings.USE_I18N or settings.USE_L10N)):
                request.session.accessed = False
                if not hasattr(request, 'ssi_patch_response'):
                    request.ssi_patch_response = []
                request.ssi_patch_response.append(ssi_vary_on_cookie)
