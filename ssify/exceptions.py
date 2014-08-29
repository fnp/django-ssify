# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
Exception classes used in django-ssify.
"""
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible


class RequestMixin(object):
    """Lets us print request and view data in the exceptions messages."""

    def __init__(self, request, *args):
        self.request = request
        super(RequestMixin, self).__init__(*args)

    def view_path(self):
        """Returns full Python path to the view used in the request."""
        try:
            view = self.request.resolver_match.func
            return "%s.%s" % (view.__module__, view.__name__)
        except AttributeError:
            return "<unknown>"


class SsifyError(RequestMixin, BaseException):
    """Base class for all the errors."""
    pass


class SsifyWarning(RequestMixin, Warning):
    """Base class for all the warnings."""
    pass


@python_2_unicode_compatible
class UndeclaredSsiVarsError(SsifyError):
    """An ssi_included view used a SSI variable, but didn't declare it."""

    def __init__(self, request, ssi_vars):
        super(UndeclaredSsiVarsError, self).__init__(request, ssi_vars)

    def __str__(self):
        return "The view '%s' at '%s' is marked as `ssi_included`, "\
            "but it uses ssi variables not declared in `get_ssi_vars` "\
            "argument: %s. " % (
                self.view_path(), self.request.get_full_path(),
                repr(self.args[0]))


@python_2_unicode_compatible
class UnusedSsiVarsWarning(SsifyWarning):
    """An ssi_included declared a SSI variable, but didn't use it."""

    def __init__(self, request, ssi_vars):
        super(UnusedSsiVarsWarning, self).__init__(request, ssi_vars)

    def __str__(self):
        return "The `ssi_included` view '%s' at '%s' declares "\
            "using SSI variables %s but it looks like they're not "\
            "really used. " % (
                self.view_path(), self.request.get_full_path(),
                self.args[0])


@python_2_unicode_compatible
class NoLangFieldError(SsifyError):
    """ssi_included views should have a `lang` field in their URL patterns."""

    def __init__(self, request):
        super(NoLangFieldError, self).__init__(request)

    def __str__(self):
        return "The view '%s' at '%s' is marked as `ssi_included` "\
            "with use_lang=True, but its URL match doesn't provide "\
            "a 'lang' keyword argument for language. " % (
                self.view_path(), self.request.get_full_path())


@python_2_unicode_compatible
class SsiVarsDependencyCycleError(SsifyError):
    """Looks like there's a dependency cycle in the SSI variables.

    Yet to find an example of a configuration that triggers that.
    """

    def __init__(self, request, ssi_vars, resolved):
        super(SsiVarsDependencyCycleError, self).__init__(
            request, ssi_vars, resolved)

    def __str__(self):
        return "The view '%s' at '%s' has dependency cycle. "\
            "Unresolved SSI variables:\n%s\n\n"\
            "Resolved SSI variables:\n%s." % (
                self.view_path(), self.request.get_full_path(),
                self.args[0], self.args[1])
