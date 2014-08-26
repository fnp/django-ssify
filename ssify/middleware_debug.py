"""
This module should only be used for debugging SSI statements.

Using DebugUnSsiMiddleware in production defeats the purpose of using SSI
in the first place, and is unsafe. You should use a proper webserver with SSI
support as a proxy (i.e. Nginx with ssi=on).

"""
import re
import urlparse
from django.core.urlresolvers import resolve
from ssify import DEBUG_VERBOSE


SSI_SET = re.compile(r"<!--#set var='(?P<var>[^']+)' "
                     r"value='(?P<value>|\\\\|.*?[^\\](?:\\\\)*)'-->", re.S)
SSI_ECHO = re.compile(r"<!--#echo var='(?P<var>[^']+)' encoding='none'-->")
SSI_INCLUDE = re.compile(r"<!--#include (?:virtual|file)='(?P<path>[^']+)'-->")
SSI_IF = re.compile(r"(?P<header><!--#if expr='(?P<expr>[^']*)'-->)"
                    r"(?P<value>.*?)(?:<!--#else-->(?P<else>.*?))?"
                    r"<!--#endif-->", re.S)
        # TODO: escaped?
SSI_VAR = re.compile(r"\$\{(?P<var>.+)\}")  # TODO: escaped?


class DebugUnSsiMiddleware(object):
    """
    Emulates a webserver with SSI support.

    This middleware should only be used for debugging purposes.
    SsiMiddleware will enable it automatically, if SSIFY_DEBUG setting
    is set to True, so you don't normally need to include it in
    MIDDLEWARE_CLASSES.

    If SSIFY_DEBUG_VERBOSE setting is True, it will also leave some
    information in HTML comments.

    """
    @staticmethod
    def _process_rendered_response(request, response):
        """Recursively process SSI statements in the response."""
        def ssi_include(match):
            """Replaces SSI include with contents rendered by relevant view."""
            path = process_value(match.group('path'))
            func, args, kwargs = resolve(path)
            parsed = urlparse.urlparse(path)
            request.META['PATH_INFO'] = request.path_info = \
                request.path = parsed.path
            request.META['QUERY_STRING'] = parsed.query
            content = func(request, *args, **kwargs).content
            content = process_content(content)
            if DEBUG_VERBOSE:
                return "".join((
                    match.group(0),
                    content,
                    match.group(0).replace('<!--#', '<!--#end-'),
                ))
            else:
                return content

        def ssi_set(match):
            """Interprets SSI set statement."""
            variables[match.group('var')] = match.group('value')
            if DEBUG_VERBOSE:
                return match.group(0)
            else:
                return ""

        def ssi_echo(match):
            """Interprets SSI echo, outputting the value of the variable."""
            content = variables[match.group('var')]
            if DEBUG_VERBOSE:
                return "".join((
                    match.group(0),
                    content,
                    match.group(0).replace('<!--#', '<!--#end-'),
                ))
            else:
                return content

        def ssi_if(match):
            """Interprets SSI if statement."""
            expr = process_value(match.group('expr'))
            if expr:
                content = match.group('value')
            else:
                content = match.group('else')
            if DEBUG_VERBOSE:
                return "".join((
                    match.group('header'),
                    content,
                    match.group('header').replace('<!--#', '<!--#end-'),
                ))
            else:
                return content

        def ssi_var(match):
            """Resolves ${var}-style variable reference."""
            return variables[match.group('var')]

        def process_value(content):
            """Resolves any ${var}-style variable references in the content."""
            return re.sub(SSI_VAR, ssi_var, content)

        def process_content(content):
            """Interprets SSI statements in the content."""
            content = re.sub(SSI_SET, ssi_set, content)
            content = re.sub(SSI_ECHO, ssi_echo, content)
            content = re.sub(SSI_IF, ssi_if, content)
            content = re.sub(SSI_INCLUDE, ssi_include, content)
            return content

        variables = {}
        response.content = process_content(response.content)
        response['Content-Length'] = len(response.content)

    def process_response(self, request, response):
        """Support for unrendered responses."""
        if hasattr(response, 'render') and callable(response.render):
            response.add_post_render_callback(
                lambda r: self._process_rendered_response(request, r)
            )
        else:
            self._process_rendered_response(request, response)
        return response
