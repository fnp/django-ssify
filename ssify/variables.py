# -*- coding: utf-8 -*-
# This file is part of django-ssify, licensed under GNU Affero GPLv3 or later.
# Copyright © Fundacja Nowoczesna Polska. See README.md for more information.
#
"""
Utilities for defining SSI variables.

SSI variables are a way of providing values that need to be computed
at request time to the prerendered templates.

"""
from __future__ import unicode_literals
from hashlib import md5
from django.template import Node
from django.template.base import get_library
from django.utils.encoding import force_text, python_2_unicode_compatible
from django.utils.functional import Promise
from django.utils.safestring import mark_safe
from .exceptions import SsiVarsDependencyCycleError


@python_2_unicode_compatible
class SsiVariable(object):
    """
    Represents a variable computed by a template tag with given arguments.

    Instance of this class is returned from any template tag created
    with `decorators.ssi_variable` decorator. If renders as SSI echo
    statement, but you can also use it as an argument to {% ssi_include %},
    to other ssi_variable, or create SSI if statements by using
    its `if`, `else`, `endif` properties.

    Variable's name, as used in SSI statements, is a hash of its definition,
    so the user never has to deal with it directly.

    """
    def __init__(self, tagpath=None, args=None, kwargs=None, name=None):
        self.tagpath = tagpath
        self.args = list(args or [])
        self.kwargs = kwargs or {}
        self._name = name

    @property
    def name(self):
        """Variable name is a hash of its definition."""
        if self._name is None:
            self._name = 'v' + md5(json_encode(self.definition).encode('ascii')).hexdigest()
        return self._name

    def rehash(self):
        """
        Sometimes there's a need to reset the variable name.

        Typically, this is the case after finding real values for
        variables passed as arguments to {% ssi_include %}.
        """
        self._name = None
        return self.name

    @property
    def definition(self):
        """Variable is defined by path to template tag and its arguments."""
        if self.kwargs:
            return self.tagpath, self.args, self.kwargs
        elif self.args:
            return self.tagpath, self.args
        else:
            return self.tagpath,

    def __repr__(self):
        return "SsiVariable(%s: %s)" % (self.name, repr(self.definition))

    def get_value(self, request):
        """Computes the real value of the variable, using the request."""
        taglib, tagname = self.tagpath.rsplit('.', 1)
        return get_library(taglib).tags[tagname].get_value(
            request, *self.args, **self.kwargs)

    def __str__(self):
        return mark_safe("<!--#echo var='%s' encoding='none'-->" % self.name)

    def as_var(self):
        """Returns the form that can be used in SSI include's URL."""
        return '${%s}' % self.name

# If-else-endif properties for use in templates.
setattr(SsiVariable, 'if',
        lambda self: mark_safe("<!--#if expr='${%s}'-->" % self.name))
setattr(SsiVariable, 'else',
        staticmethod(lambda: mark_safe("<!--#else-->")))
setattr(SsiVariable, 'endif',
        staticmethod(lambda: mark_safe('<!--#endif-->')))


class SsiExpect(object):
    """This class says: I want the real value of this variable here."""
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "SsiExpect(%s)" % (self.name,)


def ssi_expect(var, type_):
    """
    Helper function for defining get_ssi_vars on ssi_included views.

    The view needs a way of calculating all the needed variables from
    the view args. But the args are probably the wrong type
    (typically, str instead of int) or even are SsiVariables, not
    resolved until request time.

    This function provides a way to expect a real value of the needed type.

    """
    if isinstance(var, SsiVariable):
        return SsiExpect(var.name)
    else:
        return type_(var)


class SsiVariableNode(Node):
    """ Node for the SsiVariable tags. """
    def __init__(self, tagpath, args, kwargs, patch_response=None, asvar=None):
        self.tagpath = tagpath
        self.args = args
        self.kwargs = kwargs
        self.patch_response = patch_response
        self.asvar = asvar

    def __repr__(self):
        return "<SsiVariableNode>"

    def render(self, context):
        """Renders the tag as SSI echo or sets the context variable."""
        resolved_args = [var.resolve(context) for var in self.args]
        resolved_kwargs = dict((k, v.resolve(context))
                               for k, v in self.kwargs.items())
        var = SsiVariable(self.tagpath, resolved_args, resolved_kwargs)

        request = context['request']
        if not hasattr(request, 'ssi_vars_needed'):
            request.ssi_vars_needed = {}
        request.ssi_vars_needed[var.name] = var
        if self.patch_response:
            if not hasattr(request, 'ssi_patch_response'):
                request.ssi_patch_response = []
            request.ssi_patch_response.extend(self.patch_response)

        if self.asvar:
            context.dicts[0][self.asvar] = var
            return ''
        else:
            return var


def ssi_set_statement(var, value):
    """Generates an SSI set statement for a variable."""
    if isinstance(value, Promise):
        # Yes, this is quite brutal. But we need to know
        # the real value now, we don't know the type,
        # and we only want to evaluate the lazy function once.
        value = value._proxy____cast()
    if value is False or value is None:
        value = ''
    return "<!--#set var='%s' value='%s'-->" % (
        var,
        force_text(value).replace('\\', '\\\\').replace("'", "\\'"))


def provide_vars(request, ssi_vars):
    """
    Provides all the SSI set statements for ssi_vars variables.

    The main purpose of this function is to by called by SsifyMiddleware.
    """
    def resolve_expects(var):
        if not hasattr(var, 'hash_dirty'):
            var.hash_dirty = False

        for i, arg in enumerate(var.args):
            if isinstance(arg, SsiExpect):
                var.args[i] = resolved[arg.name]
                var.hash_dirty = True
        for k, arg in var.kwargs.items():
            if isinstance(arg, SsiExpect):
                var.kwargs[k] = resolved[arg.name]
                var.hash_dirty = True

        for arg in var.args + list(var.kwargs.values()):
            if isinstance(arg, SsiVariable):
                var.hash_dirty = resolve_expects(arg) or var.hash_dirty

        hash_dirty = var.hash_dirty
        if var.hash_dirty:
            # Rehash after calculating the SsiExpects with real
            # values, because that's what the included views expect.
            var.rehash()
            var.hash_dirty = False

        return hash_dirty

    def resolve_args(var):
        kwargs = {}
        for k, arg in var.kwargs.items():
            kwargs[k] = resolved[arg.name] if isinstance(arg, SsiVariable) else arg
        new_var = SsiVariable(var.tagpath,
            [resolved[arg.name] if isinstance(arg, SsiVariable) else arg for arg in var.args],
            kwargs)
        return new_var

    resolved = {}
    queue = list(ssi_vars.values())
    
    unresolved_streak = 0
    while queue:
        var = queue.pop(0)
        try:
            resolve_expects(var)
            rv = resolve_args(var)
        except KeyError as e:
            queue.append(var)
            unresolved_streak += 1
            if unresolved_streak > len(queue):
                raise SsiVarsDependencyCycleError(request, queue, resolved)
            continue

        resolved[var.name] = rv.get_value(request)
        unresolved_streak = 0

    output = "".join(ssi_set_statement(var, value)
                      for (var, value) in resolved.items()
                      ).encode('utf-8')
    return output


from .serializers import json_encode
