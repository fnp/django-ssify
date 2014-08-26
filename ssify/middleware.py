from django.conf import settings
from django.utils.cache import patch_vary_headers
from django.middleware import locale
from .serializers import json_decode, json_encode
from .variables import SsiVariable, provide_vars
from . import DEBUG


class PrepareForCacheMiddleware(object):
    @staticmethod
    def process_response(request, response):
        if getattr(request, 'ssi_vars_needed', None):
            vars_needed = {k: v.definition
                           for (k, v) in request.ssi_vars_needed.items()}
            response['X-Ssi-Vars-Needed'] = json_encode(
                vars_needed, sort_keys=True)
        return response


class SsiMiddleware(object):
    def process_request(self, request):
        request.ssi_vary = set()
        #request.ssi_cache_control_after = set()

    def process_view(self, request, view_func, view_args, view_kwargs):
        request.ssi_vars_needed = {}

    def _process_rendered_response(self, request, response):
        # Prepend the SSI variables.
        if hasattr(request, 'ssi_vars_needed'):
            vars_needed = request.ssi_vars_needed
        else:
            vars_needed = json_decode(response.get('X-Ssi-Vars-Needed', '{}'))
            vars_needed = {k: SsiVariable(*v)
                           for (k, v) in vars_needed.items()}

        if vars_needed:
            response.content = provide_vars(request, vars_needed) + \
                response.content

        # Add the Vary headers declared by all the SSI vars.
        patch_vary_headers(response, sorted(request.ssi_vary))
        # TODO: cache control?

        # With a cached response, CsrfViewMiddleware.process_response
        # was never called, so if we used the csrf token, we must do
        # its job of setting the csrf token cookie on our own.
        if (not getattr(request, 'csrf_processing_done', False)
                and request.META.get("CSRF_COOKIE_USED", False)):
            response.set_cookie(settings.CSRF_COOKIE_NAME,
                                request.META["CSRF_COOKIE"],
                                max_age=getattr(settings, 'CSRF_COOKIE_AGE',
                                                60 * 60 * 24 * 7 * 52),
                                domain=settings.CSRF_COOKIE_DOMAIN,
                                path=settings.CSRF_COOKIE_PATH,
                                secure=settings.CSRF_COOKIE_SECURE,
                                httponly=settings.CSRF_COOKIE_HTTPONLY
                                )
            request.csrf_processing_done = True

    def process_response(self, request, response):
        if hasattr(response, 'render') and callable(response.render):
            response.add_post_render_callback(
                lambda r: self._process_rendered_response(request, r)
            )
        else:
            self._process_rendered_response(request, response)

        if DEBUG:
            from .middleware_debug import DebugUnSsiMiddleware
            response = DebugUnSsiMiddleware().process_response(
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
                request.ssi_vary.add('Cookie')
